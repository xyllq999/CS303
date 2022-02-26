import pygame
import sys
import time
import random
import pickle
import numpy as np
import copy
import os
GREY=(111,111,111)
WHITE=(255,255,255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
screen_size = (800,800)
game_size=(8,8)
cube_height=screen_size[0]/game_size[0]
cube_width=screen_size[1]/game_size[1]
chess_vec=[[],[]]
candidate_list=[]
pos_dic={}
chess_count=[0,0]
pos_pos=[[],[]]
'''
q_dic={}
def load_q_data(file_name):
	with open(file_name,'r') as f:
		q_dic=pickle.load(f)
def save_q_data(file_name):
	with open(file_name,'w') as f:
		pickle.dump(q_dic,f)
def get_status_string():
	st=''
	for i in range(game_size[0]):
		for j in range(game_size[1]):
			st+=str(pos_dic[(i,j)].occupied)
	return st
def q_learning(a,y,st1,st2,choice):
	if st2 not in q_dic.keys():
		q_dic[st2]={}
	if st1 not in q_dic.keys():
		q_dic[st1]={}
	if choice not in q_dic[st1].keys():
		q_dic[st1][choice]=0
	maxi=0
	for each in q_dic[st2].keys():
		vv=q_dic[st2][each]
		if vv>maxi:
			maxi=vv
	q_dic[st1][choice]=(1-a)*q_dic[st1][choice]+a*maxi*y
'''
class one_pos():
	def __init__(self,pos):
		self.pos=pos
		self.occupied=0
		self.neighbors=[0]*8
	def occupy(self,occupied):
		##st1=get_status_string()
		self.occupied=occupied
		chess_vec[occupied-1].append(self.pos)
		ene_occupied=occupied%2+1
		chess_count[occupied-1]+=1
		if self in candidate_list:
			candidate_list.remove(self)
		for i in range(8):
			if self.neighbors[i]==0:
				continue
			if self.neighbors[i].occupied==0:
				if self.neighbors[i] not in candidate_list:
					candidate_list.append(self.neighbors[i])
			if self.neighbors[i].occupied==ene_occupied:
				current_node=self.neighbors[i]
				while 1:
					current_node=current_node.neighbors[i]
					if current_node==0:
						break
					if current_node.occupied==0:
						break
					if current_node.occupied==occupied:
						while 1:
							current_node=current_node.neighbors[(i+4)%8]
							if current_node.occupied==occupied:
								break
							current_node.occupied=occupied
							chess_vec[occupied-1].append(current_node.pos)
							chess_vec[ene_occupied-1].remove(current_node.pos)
							chess_count[occupied-1]+=1
							chess_count[ene_occupied-1]-=1
						break
		##st2=get_status_string()
		##a=0.9
		##y=0.9
		##q_learning(a,y,st1,st2,self.pos)
AI_player_list=[]
class AI_player():
	def __init__(self,para=[[],[]]):
		self.para=para
		if len(para[0])==0:
			for i in range(4):
				rand1=random.random()
				rand2=random.random()
				self.para[0].append(rand1*(i+1)*2)
				self.para[1].append(rand2*(i+1)*2)
	def merry_and_birth(self,another):
		child_para=[[[],[]],[[],[]],[[],[]],[[],[]]]
		tup=(self.para,another.para)
		for i in range(4):
			for j in range(2):
				comb=np.random.randint(0,2,4)
				for k in range(len(comb)):
					child_para[i][j].append(tup[comb[k]][j][k])
		decide=random.random()
		if decide<0.02:
			c1=np.random.randint(0,4)
			c2=np.random.randint(0,2)
			c3=np.random.randint(0,4)
			rand3=random.random()
			child_para[c1][c2][c3]=rand3*(c3+1)
		elif decide<0.12:
			c1=np.random.randint(0,4)
			c2=np.random.randint(0,2)
			c3=np.random.randint(0,4)
			randp=random.random()
			c4=np.random.randint(0,2)
			if c4==0:
				c4=-1
			child_para[c1][c2][c3]=(1+c4*0.1*randp)*child_para[c1][c2][c3]
			if child_para[c1][c2][c3]>2*(c3+1):
				child_para[c1][c2][c3]=2*(c3+1)
		for each in child_para:
			new_child=AI_player(each)
			AI_player_list.append(new_child)
		self.die()
		another.die()
	def fight(self,another,depth,execute):
		paras=(self.para,another.para)
		win_sta=[]
		for t in range(2):
			init()
			turn=t
			while 1:
				choice=AI_choice(turn,depth,paras[turn])[1]
				pos_dic[choice].occupy(turn+1)
				wini=detect_win()
				if detect_win()!=-2:
					if wini==0:
						win_sta.append(0)
					elif wini==1:
						win_sta.append(1)
					else:
						win_sta.append(-1)
					break
				turn=(turn+1)%2
				pos_pos[turn]=get_av_pos(turn)
				if len(pos_pos[turn])==0:
					turn=(turn+1)%2
					pos_pos[turn]=get_av_pos(turn)
		if execute==1:
			if win_sta[0]+win_sta[1]>0:
				another.die()
			else:
				self.die()
		else:
			return win_sta
	def die(self):
		if self in AI_player_list:
			AI_player_list.remove(self)
def draw_lines(screen):
	for i in range(1,game_size[0]):
		pygame.draw.aaline(screen, WHITE,(i*cube_height,0),(i*cube_height,screen_size[1]),5)
	for i in range(1,game_size[1]):
		pygame.draw.aaline(screen, WHITE,(0,i*cube_width),(screen_size[0],i*cube_width),5)
def draw_cubes(screen):
	for each in chess_vec[0]:
		pygame.draw.rect(screen,[0,0,0],[(each[1])*cube_width,(each[0])*cube_height,cube_width,cube_height],0)
	for each in chess_vec[1]:
		pygame.draw.rect(screen,[255,255,255],[(each[1])*cube_width,(each[0])*cube_height,cube_width,cube_height],0)
saved_list=[]
def save():
	data=pickle.dumps((candidate_list,pos_dic,chess_vec,chess_count))
	saved_list.append(data)
def load():
	global candidate_list
	global pos_dic
	global chess_vec
	global chess_count
	(candidate_list,pos_dic,chess_vec,chess_count)=pickle.loads(saved_list[-1])
def init():
	global pos_dic
	global chess_vec
	global candidate_list
	global pos_pos
	global chess_count
	pos_dic.clear()
	for i in range(game_size[0]):
		for j in range(game_size[1]):
			a_pos=one_pos((i,j))
			pos_dic[(i,j)]=a_pos
	for i in range(game_size[0]):
		for j in range(game_size[1]):
			lis=[(i,j+1),(i+1,j+1),(i+1,j),(i+1,j-1),(i,j-1),(i-1,j-1),(i-1,j),(i-1,j+1)]
			for k in range(len(lis)):
				if lis[k][0]>=0 and lis[k][0]<game_size[0] and lis[k][1]>=0 and lis[k][1]<game_size[1]:
					pos_dic[(i,j)].neighbors[k]=pos_dic[lis[k]]	
	for each in chess_vec:
		each.clear()
	chess_count=[0,0]
	candidate_list.clear()
	pos_dic[(3,3)].occupy(2)
	pos_dic[(3,4)].occupy(1)
	pos_dic[(4,3)].occupy(1)
	pos_dic[(4,4)].occupy(2)
	pos_pos[0]=get_av_pos(0)
	pos_pos[1]=get_av_pos(1)
def get_av_pos(turn):
	av_pos=[]
	ene_occupied=(turn+1)%2+1
	for each in candidate_list:
		lab=0
		for i in range(8):
			if each.neighbors[i]==0:
				continue
			if each.neighbors[i].occupied==ene_occupied:
				current_node=each.neighbors[i]
				while 1:
					current_node=current_node.neighbors[i]
					if current_node==0:
						break
					if current_node.occupied==0:
						break
					if current_node.occupied==turn+1:
						lab=1
						av_pos.append(each.pos)
						break
				if lab==1:
					break
	return av_pos
def detect_win():
	if not (len(get_av_pos(0))==0 and len(get_av_pos(1))==0):
		return -2
	##str3=get_status_string()
	if chess_count[0]==chess_count[1]:
		return 0
	if chess_count[0]>chess_count[1]:
		##q_dic[str3][(-1,-1)]=100
		return 1
	else:
		##q_dic[str3][(-1,-1)]=-100
		return -1
def evaluate(turn,emp_para,ene_para):
	ene_turn=(turn+1)%2
	val=chess_count[turn]-chess_count[ene_turn]
	for each in candidate_list:
		for i in range(8):
			if each.neighbors[i]==0:
				continue
			if each.neighbors[i].occupied==0:
				continue
			next_to=each.neighbors[i].occupied
			current_node=each.neighbors[i]
			l_count=0
			tempi=emp_para[0]
			while 1:
				current_node=current_node.neighbors[i]
				if current_node==0:
					break
				if current_node.occupied==next_to:
					l_count+=1
					continue
				if l_count>3:
					tempi1=(l_count+1)*emp_para[3]/4
					tempi2=(l_count+1)*ene_para[3]/4
				else:
					tempi1=emp_para[l_count]
					tempi2=ene_para[l_count]
				if current_node.occupied==0:
					if next_to==turn+1:
						val-=tempi1
					else:
						val+=tempi1
					break
				else:
					if next_to==turn+1:
						val-=tempi2
					else:
						val+=tempi2
					break
	return val
def min_max(turn,depth,para,min_lim=100000):
	if depth==0:
		valu=evaluate(turn,para[0],para[1])
		return (valu,(-1,-1))
	if depth==1:
		maxi=-1000000
		choici_keep=(-1,-1)
		save()
		av_pos=get_av_pos(turn)
		for each in av_pos:
			pos_dic[each].occupy(turn+1)
			vv=evaluate(turn,para[0],para[1])
			if vv>maxi:
				maxi=vv
				choici_keep=each
			load()
		saved_list.pop()
		return (maxi,choici_keep)
	max_value=-100000
	choice_keep=(-1,-1)
	ene_turn=(turn+1)%2
	save()
	av_pos1=get_av_pos(turn)	
	val2=0
	for each in av_pos1:
		pos_dic[each].occupy(turn+1)
		save()
		min_value=100000
		jian2=0
		av_pos3=get_av_pos(ene_turn)
		val2=evaluate(turn,para[0],para[1])
		min_value=val2
		for each3 in av_pos3:
			pos_dic[each3].occupy(ene_turn+1)
			val2=min_max(turn,depth-2,para,min_value)[0]
			load()
			if val2==-1000000:
				continue
			if val2<max_value:
				jian2=1
				break
			if val2<min_value:
				min_value=val2
		saved_list.pop()
		load()
		if min_value>min_lim:
			saved_list.pop()
			return (-1000000,(-1,-1))
		if jian2==1:
			continue
		if min_value!=100000 and min_value>max_value:
			max_value=min_value
			choice_keep=each
	saved_list.pop()
	return (max_value,choice_keep)	
def AI_choice(turn,depth,para):
	choice=min_max(turn,depth,para)
	return choice
def championship(size,depth):
	global AI_player_list
	print('welcome to campionship')
	while 1:
		AI_player_list2=AI_player_list.copy()
		for k in range(int(size/2)):
			print(k)
			AI_player_list2[k].fight(AI_player_list2[k+int(size/2)],depth,1)
		size=size/2
		if size<20:
			break
	counts=[]
	for i in range(len(AI_player_list)):
		counts.append(0)
	for i in range(len(AI_player_list)-1):
		for j in range(i+1,len(AI_player_list)):
			val_tup=AI_player_list[i].fight(AI_player_list[j],depth,0)
			val=val_tup[0]+val_tup[1]
			counts[i]+=val
			counts[j]+=(-1)*val
	maxi=-10000
	pos_keep=-1
	for i in range(len(counts)):
		if counts[i]>maxi:
			maxi=counts[i]
			pos_keep=i
	print('The campion para is: ',AI_player_list[i].para)
	return AI_player_list[i].para
def half_it(depth):
	AI_player_list2=AI_player_list.copy()
	for k in range(int(size/2)):
		print(k)
		AI_player_list2[k].fight(AI_player_list2[k+int(size/2)],depth,1)		
def evolution(size,generation,depth,evolute_from=[]):
	global AI_player_list
	AI_player_list.clear()
	if len(evolute_from)==0:
		for i in range(size):
			n_player= AI_player(para=[[],[]])
			AI_player_list.append(n_player)
	else:
		AI_player_list=evolute_from
	for i in range(generation):
		print('generation',i+1)
		AI_player_list2=AI_player_list.copy()
		print(i+1,': fighting.....')
		for k in range(int(size/2)):
			print(k)
			AI_player_list2[k].fight(AI_player_list2[k+int(size/2)],depth,1)
		print(i+1,': birthing.....')
		AI_player_list3=AI_player_list.copy()
		for k in range(int(size/4)):
			AI_player_list3[k].merry_and_birth(AI_player_list3[k+int(size/4)])
	##with open('group_'+str(size)+'_'+str(generation)+'_'+str(depth)+'.txt','w') as f:
	##	pickle.dump(AI_player_list,f)
	return AI_player_list
def PVP():
	init()
	pygame.init()
	screen = pygame.display.set_mode(screen_size, 0, 32)
	pygame.display.set_caption("Othello")
	FPS=30
	clock = pygame.time.Clock()
	turn=0
	win_lab=0
	while win_lab==0:
		clock.tick(FPS)
		l=0
		if pygame.mouse.get_pressed()[0]:
			pos=pygame.mouse.get_pos()
			pos_=(int(pos[1]/cube_height),int(pos[0]/cube_width))				
			if pos_ in pos_pos[turn]:
				l=1
		if l==1:
			if pos_dic[pos_].occupied==0:
				pos_dic[pos_].occupy(turn+1)
			wini=detect_win()
			if wini!=-2:
				if wini==0:
					print('tie')
				else:
					print('player ',(chess_count[0]<chess_count[1])+1,' win')
				win_lab=1
			turn=(turn+1)%2
			pos_pos[turn]=get_av_pos(turn)
			if len(pos_pos[turn])==0:
				turn=(turn+1)%2
				pos_pos[turn]=get_av_pos(turn)
		screen.fill(GREY)
		draw_lines(screen)
		draw_cubes(screen)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()	
def PVA(depth,para):
	init()
	pygame.init()
	screen = pygame.display.set_mode(screen_size, 0, 32)
	pygame.display.set_caption("Othello")
	FPS=30
	clock = pygame.time.Clock()
	turn=0
	win_lab=0
	while win_lab==0:
		clock.tick(FPS)
		l=0
		if turn==1 and pygame.mouse.get_pressed()[0]:
			pos=pygame.mouse.get_pos()
			pos_=(int(pos[1]/cube_height),int(pos[0]/cube_width))				
			if pos_ in pos_pos[turn]:
				l=1
		if turn==0:
			l=1
			pos_=AI_choice(turn,depth,para)[1]
			#time.sleep(1)
		if l==1:
			if pos_!=(-1,-1):
				if pos_dic[pos_].occupied==0:
					pos_dic[pos_].occupy(turn+1)
					print('turn ',turn,'pos ',pos_)
			wini=detect_win()
			if wini!=-2:
				if wini==0:
					print('tie')
				else:
					print('player ',(chess_count[0]<chess_count[1])+1,' win')
				win_lab=1
			turn=(turn+1)%2
			pos_pos[turn]=get_av_pos(turn)
			if len(pos_pos[turn])==0:
				turn=(turn+1)%2
				pos_pos[turn]=get_av_pos(turn)
		screen.fill(GREY)
		draw_lines(screen)
		draw_cubes(screen)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
if __name__ == "__main__":
	#PVP()
	#para1=[[0.1,0.2,0.3,0.4,0.5,0.6],[0.3,0.7,1.5,2.5,4,5]]
	#para1=[[0.9923761532085755, 1.0755606336512566, 1.4110102054839753, 0.11896724667656411], [0.8868233707446636, 1.492909894844383, 0.8938174395222604, 2.415924882666762]]
	#para1=[[1.2017835240010657,3.7022457274835725,1.130839900359228,6.4871557166996245],[0.5225696085420768,3.12737927477561,3.353022527917836,3.409391800369196]]
	#para1=[[0.8559520212400811,3.5261121688076025,5.983725759581107,5.654097808721165],[0.04612240430204295,2.1532144672397266,3.1742424484722775,4.243341471690093]]
	#para0=[[0.9839934903138061,2.5042805034313,1.0261864038769661,1.522475259355227],[1.2723463473523684,0.3977391225428817,1.5399405097644265,4.725532934722527]]
	para=[[0.9839934903138061,0.34018297112287765,1.0261864038769661,4.3603734964230565],[1.2723463473523684,0.3977391225428817,1.5399405097644265,4.725532934722527]]
	#para2=[[0.9839934903138061,0.34018297112287765,1.0261864038769661,4.3603734964230565],[1.2723463473523684,0.3977391225428817,1.5399405097644265,4.725532934722527]]
	PVA(5,para)
	time.sleep(10)
	##if os.path.exists('q_data.txt')==True:
	##	load_q_data('q_data.txt')

	paras=(para1,para2)
	win_sta=[]
	depth=2
	for t in range(2):
		init()
		turn=t
		while 1:
			choice=AI_choice(turn,depth,paras[turn])[1]
			pos_dic[choice].occupy(turn+1)
			wini=detect_win()
			if detect_win()!=-2:
				if wini==0:
					win_sta.append(0)
				elif wini==1:
					win_sta.append(1)
				else:
					win_sta.append(-1)
				break
			turn=(turn+1)%2
			pos_pos[turn]=get_av_pos(turn)
			if len(pos_pos[turn])==0:
				turn=(turn+1)%2
				pos_pos[turn]=get_av_pos(turn)
	print(win_sta)
	time.sleep(5)

	'''
	size=2000
	generation=50
	depth=1
	first_epoch=evolution(size,generation,depth)
	half_it(2)
	generation2=50
	size2=len(AI_player_list)
	depth2=2
	second_epoch=evolution(size2,generation2,depth2,AI_player_list)
	best_para=championship(size2,2)
	#best_para=championship(size,2)
	with open('3test4_para_'+str(size)+'_'+str(generation2)+'_'+str(depth2)+'.txt','w') as f:
		for i in best_para:
			for j in i:
				f.write(str(j)+'\n')
	#save_q_data('q_data.txt')
	'''
