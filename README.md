# exe_dumper

# Prerequisites
Ubuntu
Python 3.10 or higher

# Setup
- Install MinIO server (https://min.io/docs/minio/linux/index.html?ref=docs-redirect)
```commandline
cd ~
wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20240913202602.0.0_amd64.deb -O minio.deb
sudo dpkg -i minio.deb
rm -rf minio.deb
```
Check if installation is successful
```shell
mkdir ~/minio
minio server ~/minio --console-address :9001
rmdir ~/minio
```

- Start MinIO service via systemctl (https://blog.min.io/configuring-minio-with-systemd/)
```shell
groupadd -r minio-user
useradd -M -r -g minio-user minio-user
# Дальше тут надо сделать какую-то директорию и дать доступ ей minio-user
export $MINIO_OPTS="--console-address :9001"
export $MINIO_VOLUMES=<та самая директория>

sudo systemctl enable minio
sudo systemctl start minio
```
- Install Redis (https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/)
```shell
sudo apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install redis
```
- Start Redis service via systemctl
- ```shell
sudo systemctl enable redis
sudo systemctl start redis
```
