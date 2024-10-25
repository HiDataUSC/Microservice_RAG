import subprocess

class RedisManager:
    def __init__(self):
        self.distro_name = "Ubuntu"

    def is_wsl_installed(self):
        """Check if WSL is installed"""
        try:
            result = subprocess.run(["wsl", "--list", "--quiet"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def is_distro_installed(self):
        """Check if the specified distro is installed in WSL"""
        try:
            result = subprocess.run(["wsl", "--list", "--verbose"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            installed_distros = result.stdout.strip()
            return any(self.distro_name in line for line in installed_distros.splitlines())
        except FileNotFoundError:
            return False

    def is_redis_installed(self):
        """Check if Redis is installed in WSL"""
        result = subprocess.run(
            ["wsl", "-d", self.distro_name, "-u", "root", "which", "redis-server"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode == 0

    def is_redis_running(self):
        """Check if Redis server is running"""
        result = subprocess.run(
            ["wsl", "-d", self.distro_name, "-u", "root", "pgrep", "-f", "redis-server"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode == 0

    def install_wsl(self):
        """Check and install WSL and Ubuntu"""
        if not self.is_wsl_installed():
            try:
                subprocess.run(["wsl", "--install", "--no-launch"], check=True)
                print("WSL has been successfully installed")
            except subprocess.CalledProcessError as e:
                print(f"Error installing WSL: {e}")
        else:
            print("WSL is already installed")
        
        if not self.is_distro_installed():
            try:
                subprocess.run(["wsl", "--install", "-d", self.distro_name, "--no-launch"], check=True)
                print(f"{self.distro_name} has been successfully installed in WSL")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {self.distro_name}: {e}")
        else:
            print(f"{self.distro_name} is already installed in WSL")

    def install_redis(self):
        """Install Redis in WSL"""
        if self.is_redis_installed():
            print("Redis is already installed in WSL")
        else:
            try:
                # Update packages
                subprocess.run(["wsl", "-d", self.distro_name, "-u", "root", "apt", "update"], check=True)
                # Install Redis
                subprocess.run(["wsl", "-d", self.distro_name, "-u", "root", "apt", "install", "-y", "redis-server"], check=True)
                print("Redis has been successfully installed in WSL")
            except subprocess.CalledProcessError as e:
                print(f"Error installing Redis: {e}")

    def start_redis(self):
        """Start Redis server in WSL"""
        if self.is_redis_running():
            print("Redis server is already running")
        else:
            try:
                subprocess.run(["wsl", "-d", self.distro_name, "-u", "root", "redis-server", "--daemonize", "yes"], check=True)
                print("Redis has been successfully started")
            except subprocess.CalledProcessError as e:
                print(f"Error starting Redis: {e}")

    def stop_redis(self):
        """Stop Redis server in WSL"""
        if self.is_redis_running():
            try:
                subprocess.run(["wsl", "-d", self.distro_name, "-u", "root", "pkill", "-f", "redis-server"], check=True)
                print("Redis has been successfully stopped")
            except subprocess.CalledProcessError as e:
                print(f"Error stopping Redis: {e}")
        else:
            print("Redis server is not running")

    def init(self):
        """Run the full setup process"""
        self.install_wsl()
        self.install_redis()
        self.start_redis()
