# setup.sh
# DO NOT Run uintil you have edited the setup.yaml file in the docker folder
cp ../docker/setup.yaml setup.yaml
apt-get  update
apt-get install -y python-pip
pip install -r requirements.txt
apt-get install -y unzip
mkdir /tmp/creds
chmod +x gcp-setup.sh
cd ../docker
docker build -t my/app .
mkdir /tmp/Sandiego
cd /tmp/Sandiego
curl -O http://storage.googleapis.com/sandiego_freeway_gps_trips/Mobile-GPS-Trip1.csv 
curl -O  http://storage.googleapis.com/sandiego_freeway_gps_trips/Mobile-GPS-Trip10.csv 
curl -O http://storage.googleapis.com/sandiego_freeway_gps_trips/Mobile-GPS-Trip100.csv
curl -O http://storage.googleapis.com/sandiego_freeway_gps_trips/Mobile-GPS-Trip1000.csv