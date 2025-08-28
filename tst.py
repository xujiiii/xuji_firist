def aa(fuc):
    def wrapper(*args, **kwargs):
        a=fuc(*args, **kwargs)+1
        
        
        return a
    
    
    return wrapper


@aa
def pp(a):

    return a

print(pp(2))

import re 

print(re.match(r'^cf-[A-Za-z0-9]+-.+','cf-pp-o0:@";o')[0].split('-')[1])
