def generate_conflict_free_schedule(classes_list, rooms, timeslots):
    """
    A simplified scheduler that assigns classes to rooms/times 
    Round-robin logic to avoid conflicts.
    """
    schedule = []
    
    room_idx = 0
    time_idx = 0
    
    for class_name in classes_list:
        # Assign current room and time
        assigned_room = rooms[room_idx]
        assigned_time = timeslots[time_idx]
        
        schedule.append({
            "class": class_name,
            "room": assigned_room,
            "time": assigned_time
        })
        
        # Move to next room
        room_idx += 1
        
        # If we run out of rooms for this time slot, move to next time slot
        if room_idx >= len(rooms):
            room_idx = 0
            time_idx += 1
            
        # Safety check
        if time_idx >= len(timeslots):
            break
            
    return schedule