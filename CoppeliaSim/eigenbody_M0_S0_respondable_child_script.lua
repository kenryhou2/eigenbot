-- Module types
WHEEL_MODULE_TYPE = 0x01
BENDY_MODULE_TYPE = 0x03
EIGENBODY_MODULE_TYPE = 0x08
FOOT_MODULE_TYPE = 0x0A
STATIC_90_BEND_MODULE_TYPE = 0x0D

function sysCall_init()
    -- Create object handles
    eigenbot_handle=sim.getObjectHandle(sim.handle_self)    
    -- Build topology
    topology_str = buildTopologyString(eigenbot_handle)
    joint_handles = {}
    body_handle = {} --hk
    joint_positions = {}
    respondable_joint_handles = {} -- used for transforms
    initial_joint_positions = {-math.pi/4, 0.0, math.pi/4, -math.pi/4, 0.0, math.pi/4,
        -- -math.pi/4, -math.pi/4, -math.pi/4, -math.pi/4, -math.pi/4, -math.pi/4,
        -3*math.pi/8, -3*math.pi/8, -3*math.pi/8, -3*math.pi/8, -3*math.pi/8, -3*math.pi/8,
        math.pi/4, math.pi/4, math.pi/4, math.pi/4, math.pi/4, math.pi/4,}
    -- TODO get these names from topology rather than hard-coding
    for i = 1,18 do
        local joint_name = 'bendy_joint_M' .. tostring(i) .. '_S' .. tostring(i)
        joint_handles[i] = sim.getObjectHandle(joint_name)
        joint_positions[joint_name] = initial_joint_positions[i]
        local respondable_joint_name = 'bendy_output_M' .. tostring(i) .. '_S' .. tostring(i) .. '_respondable'
        respondable_joint_handles[i] = sim.getObjectHandle(respondable_joint_name)
        -- sim.setJointPosition(joint_handles[i], 0.0)
    end
    body_handle = sim.getObjectHandle('eigenbody_M0_S0_visual') --hk
    print(joint_positions)

    -- Launch the ROS client application:
    if simROS then
        sim.addLog(sim.verbosity_scriptinfos,'Successfully found ROS interface.')
        joint_cmd_sub = simROS.subscribe('/eigenbot/joint_cmd', 'sensor_msgs/JointState', 'joint_cmd_callback')
        joint_fb_pub = simROS.advertise('/eigenbot/joint_fb', 'sensor_msgs/JointState')
        joint_topology_pub = simROS.advertise('/eigenbot/topology', 'std_msgs/String')
        body_IMU_fb_pub = simROS.advertise('/eigenbot/body_IMU_fb', 'geometry_msgs/PoseStamped') --hk
    else
        sim.addLog(sim.verbosity_scripterrors,'ROS interface was not found. Cannot run.')
    end
end

function sysCall_actuation()
    for i, joint_handle in ipairs(joint_handles) do
        print(sim.getObjectName(joint_handle))
        print(joint_positions[sim.getObjectName(joint_handle)])
        sim.setJointTargetPosition(joint_handles[i], joint_positions[sim.getObjectName(joint_handle)])
    end
    print('')
    if simROS then
        -- Publish topology
        simROS.publish(joint_topology_pub, {data = topology_str})
        -- Publish joint feedback
        local joint_state = {}
        joint_state['name'] = {}
        joint_state['position'] = {}
        for i = 1,18 do
            local joint_name = 'bendy_joint_M' .. tostring(i) .. '_S' .. tostring(i)
            joint_state['name'][i] = joint_name
            
            joint_handle = joint_handles[i]
            joint_state['position'][i] = sim.getJointPosition(joint_handle)
        end
        simROS.publish(joint_fb_pub, joint_state)
        
        --Publish body IMU feedback --hk
        simROS.publish(body_IMU_fb_pub, get_pose_stamped(body_handle,sim.handle_world,'eigenbody_M0_S0_visual'))
        
        -- Send robot transforms
        local tfs = {}
        table.insert(tfs, get_transform_stamped(eigenbot_handle, 'base_link', -1, 'map'))
        for i = 1,18 do
            local respondable_joint_name = tostring(i) -- 'bendy_joint_M' .. tostring(i) .. '_S' .. tostring(i)
            if i <= 18 then
                rel_to_handle = eigenbot_handle
                rel_to_name = 'base_link'
            else
                parent_joint_idx = i - 6
                rel_to_handle = joint_handles[parent_joint_idx]
                rel_to_name = tostring(parent_joint_idx) -- 'bendy_joint_M' .. tostring(parent_joint_idx) .. '_S' .. tostring(parent_joint_idx)
            end
            table.insert(tfs, get_transform_stamped(respondable_joint_handles[i], respondable_joint_name, rel_to_handle, rel_to_name))
            -- table.insert(tfs, get_transform_stamped(respondable_joint_handles[i], respondable_joint_name, -1, 'map'))
        end
        simROS.sendTransforms(tfs)
    end
end

function sysCall_sensing()
    -- put your sensing code here
end

function sysCall_cleanup()
    -- do some clean-up here
end

function buildTopologyString(base_handle)    
    local topology = {}
    local topology_queue = {}
    table.insert(topology_queue, base_handle)
    while #topology_queue > 0 do
        local curr_obj = table.remove(topology_queue, 1)
        local curr_name = sim.getObjectName(curr_obj)
        topology[curr_name] = {}
        -- TODO support other types and orientations
        -- TODO add appropriate 'leaf' node for identifying limb type (wheel or foot)
        topology[curr_name]['type'] = (curr_name == sim.getObjectName(eigenbot_handle)) and EIGENBODY_MODULE_TYPE or BENDY_MODULE_TYPE
        topology[curr_name]['orientation'] = 1
        topology[curr_name]['children'] = {}
        local all_children = sim.getObjectsInTree(curr_obj, sim.handle_all,1+2) -- Options 1 and 2 to only get first children and exclude curr_obj
        for i,child in pairs(all_children) do
            -- Find the next corresponding joint_type child, if exists
            local child_queue = {}
            table.insert(child_queue,child)
            while #child_queue > 0 do
                local curr_child = table.remove(child_queue, 1)
                if sim.getObjectType(curr_child) == sim.object_joint_type then
                    table.insert(topology_queue, curr_child)
                    table.insert(topology[curr_name]['children'], sim.getObjectName(curr_child))
                    break
                end
                local curr_child_children = sim.getObjectsInTree(curr_child, sim.handle_all,1+2)
                for i,child_child in pairs(curr_child_children) do
                    table.insert(child_queue, child_child)
                end
            end
        end
    end
    print('Topology:')
    print(topology)
    
    -- Build topology string
    local topology_str = ''
    for module_name,module_info in pairs(topology) do
        module_info_str = '{'
        module_info_str = module_info_str .. '"id": "' .. module_name .. '", '
        module_info_str = module_info_str .. string.format('"type": "0x%x", ', module_info['type'])
        module_info_str = module_info_str .. string.format('"orientation": "0x%x", ', module_info['orientation'])
        module_info_str = module_info_str .. '"children": ['
        for i,child in pairs(module_info['children']) do
            module_info_str = module_info_str .. '"' .. child .. '"'
            if i ~= #(module_info['children']) then
                module_info_str = module_info_str .. ', '
            end
        end
        module_info_str = module_info_str .. ']},'
        topology_str = topology_str .. module_info_str
    end
    print(topology_str)
    return topology_str
end

function get_transform_stamped(obj_handle, name, rel_to, rel_to_name)
    t = simROS.getTime(); -- sim.getSystemTime()
    position = sim.getObjectPosition(obj_handle, rel_to)
    orientation = sim.getObjectQuaternion(obj_handle, rel_to)
    return {
        header={
            stamp=t,
            frame_id=rel_to_name
        },
        child_frame_id=name,
        transform={
            translation={x=position[1],y=position[2],z=position[3]},
            rotation={x=orientation[1],y=orientation[2],z=orientation[3],w=orientation[4]}
        }
    }
end

function get_pose_stamped(obj_handle, rel_to, rel_to_name)
    t = simROS.getTime();
    body_position = sim.getObjectPosition(obj_handle, rel_to) --body_position in a list of 3 cells
    quaternion = sim.getObjectQuaternion(obj_handle,rel_to) --body_quaternion in a list of 4 cells
    return{
        header={
            stamp=t,
            frame_id=rel_to_name
        },
        pose={
            position={x=body_position[1],y=body_position[2],z=body_position[3]},
            orientation={x=quaternion[1],y=quaternion[2],z=quaternion[3],w=quaternion[4]}
        }
    }
end

function joint_cmd_callback(msg)
    for i, joint_position in ipairs(msg.position) do
        -- print(#joint_positions)
        -- if i <= #joint_positions then
            joint_positions[msg.name[i]] = 1.0*joint_position
        -- end
        --[[
        if i <= #joint_handles then
            joint_handle = joint_handles[i]
            --local ret_val = sim.setJointPosition(joint_handle, 1.0)
            joint_positions[i] = 1.0*joint_position
            -- if ret_val == -1 then
            --    sim.addLog(sim.verbosity_scripterrors,'Failed to set joint position for joint: ' .. msg.name[i])
            -- end
            -- sim.addLog(sim.verbosity_scriptinfos, tostring(i) .. ' ' .. tostring(ret_val))
        end
        --]]
    end
    --sim.addLog(sim.verbosity_scripterrors, tostring(#joint_positions))
    
end

-- See the user manual or the available code snippets for additional callback functions and details
