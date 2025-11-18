RED=(255,0,0); GREEN=(0,255,0); WHITE_LOW=(60,60,60)

class RockinModes:
    def __init__(self, fixture_count=38):
        self.n=fixture_count
        self.mode=1
        self.colors=[(0,0,0)]*self.n

    def set_mode(self, m:int):
        self.mode=max(1,min(3,int(m)))

    def current_colors(self):
        return list(self.colors)

    def on_beat(self, i:int, t:float):
        if self.mode==1: self._ex1(i)
        elif self.mode==2: self._ex2(i)
        else: self._ex3(i)

    def finish_all_white_low(self):
        self.colors=[WHITE_LOW]*self.n

    def _ex1(self,k):
        phase=k%2
        for i in range(self.n):
            self.colors[i]=RED if (i%2)==phase else GREEN

    def _ex2(self,k):
        self.colors=[(0,0,0)]*self.n
        left=list(range(self.n//2-1,-1,-1))
        right=list(range(self.n//2,self.n))
        step=k%max(1,len(left))
        if step < len(left):
            a=left[step]; b=right[step] if step<len(right) else right[-1]
            col=RED if step%2==0 else GREEN
            self.colors[a]=col; self.colors[b]=col
        if k%4==3:
            for i in range(self.n): self.colors[i]=GREEN

    def _ex3(self,k):
        self.colors=[(0,0,0)]*self.n
        seg=3; steps=6; s=(k%steps)
        direction = 1 if (k%2)==0 else -1
        head = (0 if direction==1 else self.n-1) + direction*s*seg
        for j in range(seg):
            idx=(head + direction*j) % self.n
            self.colors[idx]= RED if (j%2)==0 else GREEN
        if k%8==0:
            for i in range(self.n//2): self.colors[i]=RED
            for i in range(self.n//2,self.n): self.colors[i]=GREEN
        elif k%8==1:
            for i in range(self.n//2): self.colors[i]=GREEN
            for i in range(self.n//2,self.n): self.colors[i]=RED
