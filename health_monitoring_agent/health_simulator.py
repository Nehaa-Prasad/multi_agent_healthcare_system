import random
import time
from datetime import datetime
import json
import os

class HealthDataSimulator:
    """
    Simulates realistic health monitoring data for IoT devices.
    Generates vital signs that would come from real sensors.
    """
    
    def __init__(self):
        # Realistic medical ranges for vital signs
        self.heart_rate_range = (60, 100)        # BPM (beats per minute)
        self.bp_systolic_range = (90, 140)       # mmHg (millimeters of mercury)
        self.bp_diastolic_range = (60, 90)       # mmHg
        self.oxygen_range = (95, 100)            # % oxygen saturation
        self.temperature_range = (36.1, 37.2)    # Celsius
        self.respiratory_rate_range = (12, 20)   # breaths per minute
        
        # For more realistic data - sometimes add slight variations
        self.variation_factor = 0.1  # 10% variation
        
        # Data storage
        self.data_file = os.path.join(os.getcwd(), "data", "vitals_stream.json")
        self.ensure_data_directory()
        
    def generate_vitals(self):
        """
        Generate a single set of realistic vital signs.
        Returns a dictionary with timestamp and all vital signs.
        """
        # Add some realistic variation (not completely random)
        heart_rate = self._add_variation(random.randint(*self.heart_rate_range))
        bp_systolic = self._add_variation(random.randint(*self.bp_systolic_range))
        bp_diastolic = self._add_variation(random.randint(*self.bp_diastolic_range))
        oxygen = round(random.uniform(*self.oxygen_range), 1)
        temperature = round(random.uniform(*self.temperature_range), 1)
        respiratory_rate = self._add_variation(random.randint(*self.respiratory_rate_range))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'heart_rate': heart_rate,
            'bp_systolic': bp_systolic,
            'bp_diastolic': bp_diastolic,
            'oxygen_saturation': oxygen,
            'temperature': temperature,
            'respiratory_rate': respiratory_rate,
            'device_id': 'health_sensor_001'  # Simulate device ID
        }
    
    def _add_variation(self, value):
        """Add small random variation to make data more realistic"""
        variation = random.uniform(-self.variation_factor, self.variation_factor)
        return int(value * (1 + variation))
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs("data", exist_ok=True)
    
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
    
    def generate_abnormal_vitals(self):
        """
        Generate abnormal vital signs for testing alert systems.
        This simulates emergency situations.
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'heart_rate': random.randint(110, 150),  # High heart rate
            'bp_systolic': random.randint(150, 200), # High blood pressure
            'bp_diastolic': random.randint(95, 120), # High diastolic
            'oxygen_saturation': round(random.uniform(85, 94), 1),  # Low oxygen
            'temperature': round(random.uniform(38.0, 40.0), 1),    # Fever
            'respiratory_rate': random.randint(25, 35),  # High respiratory rate
            'device_id': 'health_sensor_001',
            'alert_level': 'CRITICAL'
        }
    
    def run_continuous_simulation(self, duration_seconds=60, interval=1):
        """
        Run continuous simulation for specified duration.
        
        Args:
            duration_seconds: How long to run (default 60 seconds)
            interval: Time between readings in seconds (default 1 second)
        """
        print("🏥 Starting Health Data Simulation...")
        print("=" * 50)
        print(f"📁 Data will be saved to: {self.data_file}")
        
        end_time = time.time() + duration_seconds
        reading_count = 0
        
        while time.time() < end_time:
            reading_count += 1
            
            # 90% normal data, 10% abnormal data for testing
            if random.random() < 0.9:
                vitals = self.generate_vitals()
                status = "✅ NORMAL"
            else:
                vitals = self.generate_abnormal_vitals()
                status = "🚨 ABNORMAL"
            
            # Save to JSON file
            self.save_to_json(vitals)
            
            # Print formatted output
            print(f"\n{status} - {vitals['timestamp']} (Reading #{reading_count})")
            print(f"💓 Heart Rate: {vitals['heart_rate']} BPM")
            print(f"🩸 Blood Pressure: {vitals['bp_systolic']}/{vitals['bp_diastolic']} mmHg")
            print(f"🫁 Oxygen: {vitals['oxygen_saturation']}%")
            print(f"🌡️  Temperature: {vitals['temperature']}°C")
            print(f"🫁 Respiration: {vitals['respiratory_rate']} BPM")
            
            time.sleep(interval)
        
        print("\n" + "=" * 50)
        print("✅ Simulation completed!")
        print(f"📊 Total readings saved: {reading_count}")
        print(f"📁 Data saved to: {self.data_file}")
    
    def run_single_reading(self):
        """Generate a single reading for testing"""
        vitals = self.generate_vitals()
        self.save_to_json(vitals)
        print("📊 Single Health Reading:")
        print(json.dumps(vitals, indent=2))
        print(f"📁 Data saved to: {self.data_file}")
        return vitals

def main():
    """Main function to test the simulator"""
    print("Health Data Simulator - Test Mode")
    print("Choose an option:")
    print("1. Single reading")
    print("2. 10-second simulation")
    print("3. 1-minute simulation")
    
    choice = input("Enter choice (1-3): ").strip()
    
    simulator = HealthDataSimulator()
    
    if choice == "1":
        simulator.run_single_reading()
    elif choice == "2":
        simulator.run_continuous_simulation(10)
    elif choice == "3":
        simulator.run_continuous_simulation(60)
    else:
        print("Invalid choice. Running single reading...")
        simulator.run_single_reading()

if __name__ == "__main__":
    main()
