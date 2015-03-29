import datetime
import os
c_time=datetime.datetime.now()
e_time=c_time + datetime.timedelta(seconds=850)
while(e_time>=datetime.datetime.now()):
    #os.system("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndwr run")
    #os.system("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndwr cleanup")
    f=open("/home/data/data.txt","w+")
    file_content=f.read()
    print(file_content)
    f.write("qwew fsdlj gf ggf gh hj gf gf fd hj hj fsa fas fh fsd gh fsd gh gf gf hfsd gg bhfdh sdg g hgfhmfd hgdhgf gfgfgfgf gfffff gfgfhgj ghhhhh ghhhhhhhh gfffffff gffffff gffffffffffd ghhhhhhhhhhhhh gffffffffffffff hggggggggggggggggg ghhhhhhhhhhhhhh fggggggggggg hgggggggggggggggggggggg ghhhhhhhhhhhhhhhhhhhhhh ggggggggggggggggggggggggggf gf;klfkdlgf llg sdjkljkl ;klgfkl;jklgf ;kll;gf;l gf;klfd;klfd ;l;kl;kl kl;kl;kll ;kl;klgklgfkl kldfklffklfdklfhd")
    f.close()
