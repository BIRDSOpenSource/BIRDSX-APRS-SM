import serial
import time

# Main function
def main():
    #output_file_path = '/home/birdsx/test/output_data.dat'
    output_file_path = '/home/birdsx/Desktop/APRS_WS/output_de.txt'
    output_file_path2 = '/home/birdsx/Desktop/APRS sensor data/output_data_APRS.dat'
    output_file_path3 = '/home/birdsx/Desktop/APRS sensor data/output_data_timestamp.dat'
    session_file_path = '/home/birdsx/Desktop/APRS sensor data/session_count.txt'

    ser = serial.Serial("/dev/ttyACM0", 9600)
    
    capture_data = False  # Initialize flag to False
    wind_speed = None  # Initialize wind_speed variable outside the loop
    wind_speed_acc = None 
    trend_data = None
    
    # Read the session count from the file
    try:
        with open(session_file_path, 'r') as session_file:
            run_count = int(session_file.read().strip())
    except FileNotFoundError:
        run_count = 0  # Set run_count to 0 if the file doesn't exist
    
    with open(output_file_path, 'w') as file1, open(output_file_path2, 'a') as file2, open(output_file_path3, 'a') as file3:
    
        start_time = time.time()  # Record the start time
        try:
            while True:
                data = ser.readline().decode("utf-8").strip()
                
                callsign_src = 'APRSGT'
                callsign_des = 'JG6Y0W-11'
                digi_path = 'WIDE1-1'
                timestamp = time.strftime('%H%M%S')
                #timestamp = time.strftime('%d-%m-%Y %H:%M')
                lat = '3250.49N'
                lon = '13101.47E'

                # Check if the row starts with wind speed data
                #if data.startswith(('00', '01', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if data.startswith(('Temperature', 'SO2')):
                    trend_data = data
                    print(trend_data)
                    continue
                
                if len(data) == 3:
                    wind_speed = data
                    #print(wind_speed)
                    continue  # Skip to the next iteration to read the next line
                    
                if data.startswith(('0.', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    wind_speed_acc = data
                    print(wind_speed_acc)
                    continue  # Skip to the next iteration to read the next line
                    
                
                if wind_speed:
                    # Insert wind speed after the '/'
                    parts = data.split('/')
                    if len(parts) == 2:
                        aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_{parts[0]}/{wind_speed}{parts[1]}'
                        #if trend_data:
                        #    aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_{parts[0]}/{wind_speed}{parts[1]}{trend_data}'
                        #    trend_data = None
                        if wind_speed_acc :
                            aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_{parts[0]}/{wind_speed}{parts[1]}wsa{wind_speed_acc}'
                            wind_speed_acc  = None
                        #if trend_data and wind_speed_acc :
                        #    aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_{parts[0]}/{wind_speed}{parts[1]}{wind_speed_acc}{trend_data}'
                        #    trend_data = None
                        #    wind_speed_acc  = None
                    else:
                        # Handle the case where the data format is unexpected
                        aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_{wind_speed}{data}'
                    wind_speed = None  # Reset wind_speed after using it
                else:
                    
                    # No wind speed row, add wind speed of zero to each row
                    #aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_0.00{data}'
                    
                    parts = data.split('/')
                    if len(parts) == 2:
                        aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_{parts[0]}/000{parts[1]}'
                
                        #if trend_data:
                        #    aprs_data = f'{callsign_src}>{callsign_des},{digi_path}:@{timestamp}z{lat}/{lon}_{parts[0]}/000{parts[1]}{trend_data}'
                        #    trend_data = None
                        
                
                if capture_data:
                    file1.write(aprs_data + '\n')  # Use file1 for the first file
                    file1.flush()  # Ensure data is immediately saved to the file
                    file2.write(aprs_data + '\n')  # Use file2 for the second file
                    file2.flush()  # Ensure data is immediately saved to the file
                    
                    timestamp_hours = timestamp[:2]
                    timestamp_minutes = timestamp[2:4]
                    timestamp_seconds = timestamp[4:]
                    timestamp_ddmmyy = time.strftime('%d/%m/%y')
                    timestamp_formatted = f'{timestamp_ddmmyy} {timestamp_hours}:{timestamp_minutes}:{timestamp_seconds}'
                    
                    file3.write(timestamp_formatted + '\n')  # Use file2 for the second file
                    file3.flush()  # Ensure data is immediately saved to the file
                    #capture_data = False
                    print(data)
                
                # Check if 1 second has passed since the start time
                if not capture_data and time.time() - start_time >= 1:
                    
                    # Increment run count and write session information to file2
                    run_count += 1
                    current_time = time.strftime('%H:%M:%S %d/%m/%y')
                    file2.write(f'SESSION {run_count}\n')
                    file2.write(f'Start Time: {current_time}\n')
                    file2.flush()
                    file3.write(f'SESSION {run_count}\n')
                    file3.write(f'Start Time: {current_time}\n')
                    file3.flush()
                    capture_data = True
                    
                    # Update the run count value in the text file
                    with open(session_file_path, 'w') as session_file:
                        session_file.write(str(run_count))
                    
        except KeyboardInterrupt:
            # Handle Ctrl+C: Write stop time and duration before exiting
            stop_time = time.strftime('%H:%M:%S %d/%m/%y')
            duration = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time - 6))
            file2.write(f'Stop Time: {stop_time}, Duration: {duration}\n')
            file2.write('  \n')
            file2.flush()
            file3.write(f'Stop Time: {stop_time}, Duration: {duration}\n')
            file3.write('  \n')
            file3.flush()
            print("Exiting...")
            sys.exit()
                    
         
if __name__ == "__main__":
    main()
