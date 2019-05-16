import subprocess
import tqdm
import os
from subprocess import PIPE, Popen

def extract_assemnbly_instruction(target):    
    '''
    reference: https://cnpnote.tistory.com/entry/PYTHON-%EC%B4%88%EB%B3%B4%EC%9E%90-%ED%8C%8C%EC%9D%B4%EC%8D%AC-%ED%95%98%EC%9C%84-%ED%94%84%EB%A1%9C%EC%84%B8%EC%8A%A4-%EC%93%B0%EA%B8%B0-%EC%98%A4%EB%A5%98-%EB%B8%8C%EB%A1%9C%ED%81%B0-%ED%8C%8C%EC%9D%B4%ED%94%84
    '''
    #params is "objdump -d {} | grep '[0-9a-z]\{6\}:' | cut -b 33-50 | cut -d ' ' -f 1 | sort | awk NF | uniq".format(target)
    p1 = Popen(['objdump', '-d', target], stdout=PIPE) #objdmp -d
    p2 = Popen(['grep', '[0-9a-z]\{6\}:'], stdin=p1.stdout, stdout=PIPE) # grep '[0-9a-z]\{6\}:'
    p3 = Popen(['cut', '-b', '33-50'], stdin=p2.stdout, stdout=PIPE) # cut -b 33-50
    p4 = Popen(['cut', '-d', ' ', '-f', '1'], stdin=p3.stdout, stdout=PIPE) # cut -d ' ' -f 1
    p5 = Popen(['sort'], stdin=p4.stdout, stdout=PIPE) # sort
    p6 = Popen(['awk', 'NF'], stdin=p5.stdout, stdout=PIPE)

    stdout_value = p6.communicate()[0].decode('utf-8')
    stdout_list = stdout_value.rstrip('\n').splitlines()

    return stdout_list

def main():
    dirpath = '/home/choi/Desktop/TrainTest'
    sample = '0a21a5b990c3e39d8744dc0e323b0d7d.vir'
    target = os.path.join(dirpath, sample)

    asm_instruction_dict = {}
    asm_instruction_list = extract_assemnbly_instruction(target)
    
    for instruction in asm_instruction_list:
        if asm_instruction_dict.get(instruction):   
            asm_instruction_dict[instruction] += 1
        else:
            asm_instruction_dict[instruction] = 1

    for key, value in asm_instruction_dict.items():
        print('{}: {}'.format(key, value))

if __name__ == '__main__':
    main()