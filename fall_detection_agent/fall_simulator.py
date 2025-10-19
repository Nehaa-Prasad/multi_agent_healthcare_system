import random
import time
import math
from datetime import datetime
import json
import os

class FallDetectionSimulator:
    """
    Simulates accelerometer data for fall detection.
    Generates realistic x, y, z coordinate data that would come from IoT sensors.
    """
    
    def __init__(self):
        # Gravity constant (9.8 m/s²) - accelerometer measures in g-force
        self.gravity = 9.8
        
        # Normal movement ranges (in g-force units)
        self.normal_x_range = (-0.5, 0.5)    # Side to side movement
        self.normal_y_range = (-0.5, 0.5)    # Forward/backward movement  
        self.normal_z_range = (0.7, 1.3)     # Up/down (gravity + small movements)
        
        # Fall detection thresholds
        self.fall_threshold = 2.5  # g-force above this indicates potential fall
        self.impact_threshold = 3.0  # g-force above this indicates impact
        
        # Inactivity threshold (seconds of no significant movement)
        self.inactivity_threshold = 30
        
        # Data storage
        self.data_file = os.path.join(os.getcwd(), "data", "fall_events.json")
        self.ensure_data_directory()
        
    def generate_normal_movement(self):
        """
        Generate accelerometer data for normal activities.
        Simulates walking, sitting, standing, gentle movements.
        """
        # Add some realistic variation to simulate natural movement
        x = random.uniform(*self.normal_x_range) + random.uniform(-0.1, 0.1)
        y = random.uniform(*self.normal_y_range) + random.uniform(-0.1, 0.1)
        z = random.uniform(*self.normal_z_range) + random.uniform(-0.1, 0.1)
        
        # Calculate total acceleration magnitude
        magnitude = math.sqrt(x*x + y*y + z*z)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'x': round(x, 3),
            'y': round(y, 3),
            'z': round(z, 3),
            'magnitude': round(magnitude, 3),
            'activity': 'NORMAL',
            'device_id': 'fall_sensor_001'
        }
    
    def generate_fall_pattern(self):
        """
        Generate accelerometer data that simulates a fall.
        Creates a sudden drop followed by impact.
        """
        # Phase 1: Sudden drop (free fall) - low acceleration
        drop_x = random.uniform(-0.2, 0.2)
        drop_y = random.uniform(-0.2, 0.2)
        drop_z = random.uniform(0.1, 0.3)  # Low z indicates falling
        
        # Phase 2: Impact - high acceleration in all directions
        impact_x = random.uniform(-self.impact_threshold, self.impact_threshold)
        impact_y = random.uniform(-self.impact_threshold, self.impact_threshold)
        impact_z = random.uniform(self.impact_threshold, self.impact_threshold + 2)
        
        # Choose between drop phase or impact phase
        if random.random() < 0.3:  # 30% chance of impact phase
            x, y, z = impact_x, impact_y, impact_z
            activity = 'FALL_IMPACT'
        else:  # 70% chance of drop phase
            x, y, z = drop_x, drop_y, drop_z
            activity = 'FALL_DROP'
        
        magnitude = math.sqrt(x*x + y*y + z*z)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'x': round(x, 3),
            'y': round(y, 3),
            'z': round(z, 3),
            'magnitude': round(magnitude, 3),
            'activity': activity,
            'device_id': 'fall_sensor_001',
            'alert_level': 'HIGH' if magnitude > self.fall_threshold else 'MEDIUM'
        }
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs("../data", exist_ok=True)
    
    def save_to_json(self, data):
        """Save data to JSON file"""
        try:
            # Load existing data
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = []
            
            # Add new data
            all_data.append(data)
            
            # Save back to file
            with open(self.data_file, 'w') as f:
                json.dump(all_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def generate_inactivity_pattern(self):
        """
        Generate data for inactive periods (person not moving much).
        Simulates sleeping, sitting still, etc.
        """
        # Very small movements, mostly just gravity
        x = random.uniform(-0.1, 0.1)
        y = random.uniform(-0.1, 0.1)
        z = random.uniform(0.9, 1.1)  # Close to gravity
        
        magnitude = math.sqrt(x*x + y*y + z*z)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'x': round(x, 3),
            'y': round(y, 3),
            'z': round(z, 3),
            'magnitude': round(magnitude, 3),
            'activity': 'INACTIVE',
            'device_id': 'fall_sensor_001'
        }
    
    def generate_walking_pattern(self):
        """
        Generate data that simulates walking motion.
        Creates rhythmic patterns typical of walking.
        """
        # Walking creates rhythmic up-down motion
        time_factor = time.time() * 2  # Speed of walking rhythm
        walking_z = 1.0 + 0.3 * math.sin(time_factor)  # Up-down motion
        walking_x = 0.2 * math.sin(time_factor * 0.5)  # Side-to-side sway
        walking_y = 0.1 * math.cos(time_factor * 0.3)  # Forward-backward
        
        magnitude = math.sqrt(walking_x*walking_x + walking_y*walking_y + walking_z*walking_z)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'x': round(walking_x, 3),
            'y': round(walking_y, 3),
            'z': round(walking_z, 3),
            'magnitude': round(magnitude, 3),
            'activity': 'WALKING',
            'device_id': 'fall_sensor_001'
        }
    
    def run_continuous_simulation(self, duration_seconds=60, interval=0.5):
        """
        Run continuous simulation with different movement patterns.
        
        Args:
            duration_seconds: How long to run (default 60 seconds)
            interval: Time between readings in seconds (default 0.5 seconds)
        """
        print("🚶 Starting Fall Detection Simulation...")
        print("=" * 60)
        print(f"📁 Data will be saved to: {self.data_file}")
        
        end_time = time.time() + duration_seconds
        reading_count = 0
        
        while time.time() < end_time:
            reading_count += 1
            
            # Different patterns based on reading count
            if reading_count % 20 == 0:  # Every 20th reading - potential fall
                data = self.generate_fall_pattern()
                status = "🚨 FALL DETECTED"
            elif reading_count % 15 == 0:  # Every 15th reading - walking
                data = self.generate_walking_pattern()
                status = "🚶 WALKING"
            elif reading_count % 10 == 0:  # Every 10th reading - inactive
                data = self.generate_inactivity_pattern()
                status = "😴 INACTIVE"
            else:  # Most readings - normal movement
                data = self.generate_normal_movement()
                status = "✅ NORMAL"
            
            # Save to JSON file
            self.save_to_json(data)
            
            # Print formatted output
            print(f"\n{status} - {data['timestamp']} (Reading #{reading_count})")
            print(f"📊 Accelerometer: X={data['x']:>6}, Y={data['y']:>6}, Z={data['z']:>6}")
            print(f"📏 Magnitude: {data['magnitude']:>6} g")
            print(f"🏷️  Activity: {data['activity']}")
            
            # Show alert if magnitude is high
            if data['magnitude'] > self.fall_threshold:
                print(f"⚠️  ALERT: High acceleration detected! ({data['magnitude']:.2f} g)")
            
            time.sleep(interval)
        
        print("\n" + "=" * 60)
        print("✅ Fall detection simulation completed!")
        print(f"📊 Total readings saved: {reading_count}")
        print(f"📁 Data saved to: {self.data_file}")
    
    def run_single_reading(self, pattern='normal'):
        """Generate a single reading for testing"""
        if pattern == 'fall':
            data = self.generate_fall_pattern()
        elif pattern == 'walking':
            data = self.generate_walking_pattern()
        elif pattern == 'inactive':
            data = self.generate_inactivity_pattern()
        else:
            data = self.generate_normal_movement()
        
        # Save to JSON file
        self.save_to_json(data)
        
        print(f"📊 Single Accelerometer Reading ({pattern.upper()}):")
        print(json.dumps(data, indent=2))
        print(f"📁 Data saved to: {self.data_file}")
        return data

def main():
    """Main function to test the simulator"""
    print("Fall Detection Simulator - Test Mode")
    print("Choose an option:")
    print("1. Single normal reading")
    print("2. Single fall reading")
    print("3. Single walking reading")
    print("4. Single inactive reading")
    print("5. 10-second simulation")
    print("6. 1-minute simulation")
    
    choice = input("Enter choice (1-6): ").strip()
    
    simulator = FallDetectionSimulator()
    
    if choice == "1":
        simulator.run_single_reading('normal')
    elif choice == "2":
        simulator.run_single_reading('fall')
    elif choice == "3":
        simulator.run_single_reading('walking')
    elif choice == "4":
        simulator.run_single_reading('inactive')
    elif choice == "5":
        simulator.run_continuous_simulation(10)
    elif choice == "6":
        simulator.run_continuous_simulation(60)
    else:
        print("Invalid choice. Running single normal reading...")
        simulator.run_single_reading('normal')

if __name__ == "__main__":
    main()
