import datetime
c_time=datetime.datetime.now()
e_time=c_time + datetime.timedelta(seconds=600)
while(e_time>=datetime.datetime.now()):
    f=open("/home/baadalvm/Desktop/data/data.txt","w+")
    file_content=f.read()
    print(file_content)
    f.write("qwew fsdlj gf ggf gh hj gf gf fd hj hj fsa   fas fh fsd gh fsd gh gf gf hfsd gg bhfdh sdg g hgfhmfd  hgdhgf gfgfgfgf gfffff    gfgfhgj  ghhhhh ghhhhhhhh gfffffff gffffff gffffffffffd ghhhhhhhhhhhhh gffffffffffffff hggggggggggggggggg ghhhhhhhhhhhhhh fggggggggggg hgggggggggggggggggggggg ghhhhhhhhhhhhhhhhhhhhhh ggggggggggggggggggggggggggf  gf;klfkdlgf llg sdjkljkl ;klgfkl;jklgf ;kll;gf;l gf;klfd;klfd ;l;kl;kl kl;kl;kll ;kl;klgklgfkl kldfklffklfdklfhd")
    f.close()
