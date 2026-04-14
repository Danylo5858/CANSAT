import subprocess
from csv import reader

def get_backup_data(req_data):
	try:
		result = subprocess.run(
			["./get_backup_data.sh"],
			check=True,
			capture_output=True,
			text=True
		)
		print("Copia de seguridad del CanSat recibida correctamente")
	except subprocess.CalledProcessError as e:
		print(f"Fallo recibiendo la copia de seguridad del CanSat:\nCodigo: {result.returncode}\nError: {result.stderr}")
		return { "success": False }

	bmp_data = []
	mpu_data = []
	gps_data = []
	final_data = { "success": True, "data": {} }
	if req_data["bmp"]:
		print("1")
		with open('./BackupData/BMP390_data.csv', 'r', newline='') as f:
			print("2")
			data_reader = reader(f)
			for row in data_reader:
				print("3")
				data = {
		            "date": row[0],
		            "time": row[1],
		            "temperature": float(row[2]),
		            "pressure": float(row[3]),
		            "altitude": float(row[4]),
		        }
				if ValidateTime(req_data, data):
					bmp_data.append(data)
		final_data["data"]["BMP390"] = bmp_data
	if req_data["mpu"]:
		with open('./BackupData/MPU6050_data.csv', 'r', newline='') as f:
			data_reader = reader(f)
			for row in data_reader:
				data = {
		            "date": row[0],
		            "time": row[1],
		            "quats": row[2]
		        }
				if ValidateTime(req_data, data):
					mpu_data.append(data)
		final_data["data"]["MPU6050"] = mpu_data
	if req_data["gps"]:
		with open('./BackupData/GPS_data.csv', 'r', newline='') as f:
			data_reader = reader(f)
			for row in data_reader:
				data = {
		            "date": row[0],
		            "time": row[1],
		            "latitude": float(row[2]),
		            "longitude": float(row[3]),
		            "satellites": float(row[4])
		        }
				if ValidateTime(req_data, data):
					gps_data.append(data)
		final_data["data"]["GPS"] = gps_data
	return final_data

def ValidateTime(req_data, data):
	print("4")
	if req_data["start"] != 0 or req_data["end"] != 0:
		if req_data["start"] <= (data["date"] + " " + data["time"]) <= req_data["end"]:
			print("TRUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
			return True
		else:
			return False
	else:
		return True
