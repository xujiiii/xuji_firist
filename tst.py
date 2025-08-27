def aa(fuc):
    def wrapper(*args, **kwargs):
        a=fuc(*args, **kwargs)+1
        
        
        return a
    
    
    return wrapper


@aa
def pp(a):

    return a

print(pp(2))

