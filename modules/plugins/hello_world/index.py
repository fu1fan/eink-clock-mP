import time



def init(env):
    def debug(env):
        time.sleep(2)
        pass    #在这里打断点
    print("Hello world!")
    env.pool.add(debug, env)