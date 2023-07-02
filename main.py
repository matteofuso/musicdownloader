from libs import enviroment

# Check if  the environment variable is set correctly
enviroment.init()

# If the script is not running as a module 
if __name__ == '__main__':
    print("Hello")