from tkinter import *
from tkinter import messagebox, ttk, Toplevel
from random import randint
from datetime import datetime
import os

class CONST:
    w = 800
    h = 279

class MainMenu(ttk.Frame):
    def __init__(self):
        super().__init__()

        self.curScore = 0
        self.curDiff = IntVar()
        self.curDiff.set(1)

        self.__triangleDebuff_cancellationFunctionCallbackId = -1
        self.__triangleDebuffApplied = False

        self.initUI()
    
    def initUI(self):
        def reset():##
            open('records.txt', 'w').close()
            pass

        self.master.title("Falling Nuts")
        self.master.resizable(0,0)
        self.master.option_add('*tearOff', FALSE)#Чтобы меню не отрывались

        sstyle = ttk.Style()
        bstyle = ttk.Style()
        istyle = ttk.Style()

        sstyle.configure('namelabel.TLabel', font=('Times New Roman', '43'))
        bstyle.configure('usualbutton.TButton', font=('Times New Roman', '20'))
        istyle.configure('bigquestionbutton.TButton', font=('Times New Roman', '80'), width=1)
        
        label = ttk.Label(self, text="Falling Nuts", style='namelabel.TLabel')
        butStart = ttk.Button(self, text="Start", command=self.game, style='usualbutton.TButton')
        butLeader = ttk.Button(self, text="Leaderboard", command=self.leaderboard, style='usualbutton.TButton')
        butExit = ttk.Button(self, text="Exit", command=self.quit, style='usualbutton.TButton')
        butInq = ttk.Button(self, text="?", command=self.inquiry, style='bigquestionbutton.TButton')

        label.grid(row=0,columnspan=2)
        butStart.grid(row=1, column=0)
        butLeader.grid(row= 2, column=0)
        butExit.grid(row= 3, column=0)
        butInq.grid(column=1,row=1, rowspan=3, sticky='WE')

        menubar = Menu(self.master)
        menu_diff = Menu(menubar)

        menu_diff.add_radiobutton(label='Easy', variable=self.curDiff, value=1)
        menu_diff.add_radiobutton(label='Medium', variable=self.curDiff, value=2)
        menu_diff.add_radiobutton(label='Hard', variable=self.curDiff, value=3)

        menubar.add_cascade(menu=menu_diff, label='Difficulty')

        menubar.add_command(label='Reset', command=reset)

        self.master['menu'] = menubar

        self.grid(sticky="NSWE")

    def game(self):
        ##FUNCTIONS
        def gameloop(*args):
            if self.itemsOnScreen_regular < self.maxItems_regular:
                canv.after(randint(spawnInterval[0], spawnInterval[1])*1000, newItem_regular)
                self.itemsOnScreen_regular += 1
            
            if self.itemsOnScreen_irregular < self.maxItems_irregular:
                canv.after(randint(spawnInterval[0], spawnInterval[1])*1000, newItem_irregular)
                self.itemsOnScreen_irregular += 1

            if self.itemsOnScreen_line < self.maxItems_line:
                if randint(1, 100) <= self.generationChance_line:
                    canv.after(randint(spawnInterval[0], spawnInterval[1])*1000, newItem_line)
                    self.itemsOnScreen_line += 1

            if self.itemsOnScreen_triangle < self.maxItems_triangle:
                if randint(1, 100) <= self.generationChance_triangle:
                    canv.after(randint(spawnInterval[0], spawnInterval[1])*1000, newItem_triangle)
                    self.itemsOnScreen_triangle += 1
            
            for item in canv.find_withtag('fall_reg'):
                canv.move(item, 0, 1)
                if canv.coords(item)[3] >= CONST.h:
                    canv.delete(item)
                    if updLives(-1) == 1:
                        onClose()
                        return
                    self.itemsOnScreen_regular -= 1
                    flicker_widget_background(widget=curLives, newColor='red', newColor2='black', oldColor='black', frequency=200, times_to_flicker= 4)
                elif canv.coords(item)[3] >= canv.coords(rect2)[1] and ((canv.coords(item)[0] >= canv.coords(rect2)[0] and canv.coords(item)[0] <= canv.coords(rect2)[2]) or (canv.coords(item)[2] <= canv.coords(rect2)[2] and canv.coords(item)[2] >= canv.coords(rect2)[0])):
                    canv.delete(item)
                    updScore(1)
                    self.itemsOnScreen_regular -= 1
                    flicker_canvasitem_fill(itemId=rect2, newColor='yellow', newColor2='blue', oldColor='blue', frequency=100, times_to_flicker= 4)
                    flicker_widget_background(widget=curScore, newColor='yellow', newColor2='black', oldColor='black', frequency=200, times_to_flicker= 4)

            for item in canv.find_withtag('fall_irreg'):
                #Название второго тега (canv.gettags(item)[1])) используется для хранения значения float для определения скорости падения объекта (canv.move())
                canv.move(item, 0, float(canv.gettags(item)[1]))
                
                if canv.coords(item)[3] >= CONST.h:
                    canv.delete(item)
                    self.itemsOnScreen_irregular -= 1
                elif canv.coords(item)[3] >= canv.coords(rect2)[1] and ((canv.coords(item)[0] >= canv.coords(rect2)[0] and canv.coords(item)[0] <= canv.coords(rect2)[2]) or (canv.coords(item)[2] <= canv.coords(rect2)[2] and canv.coords(item)[2] >= canv.coords(rect2)[0])):
                    canv.delete(item)
                    if updLives(-2) == 1:
                        onClose()
                        return
                    self.itemsOnScreen_irregular -= 1
                    flicker_canvasitem_fill(itemId=rect2, newColor='red', newColor2='blue', oldColor='blue', frequency=100, times_to_flicker= 8)
                    flicker_widget_background(widget=curLives, newColor='red', newColor2='black', oldColor='black', frequency=200, times_to_flicker= 4)

            for item in canv.find_withtag('triangle'):
                canv.move(item, int(canv.gettags(item)[1]), 1)
                self.catcher_coords = canv.coords(rect2)
                self.item_coords = canv.coords(item)
                margin = ((self.item_coords[5] - self.catcher_coords[1]) - (self.catcher_coords[1]) - self.item_coords[1])/(self.item_coords[5] - self.catcher_coords[1])
                margin *= self.item_coords[0] - self.item_coords[2]
                margin = ((self.item_coords[0] - self.item_coords[2]) - margin)/2
                if self.item_coords[5] >= CONST.h:
                    canv.delete(item)
                    self.itemsOnScreen_triangle -= 1
                elif self.item_coords[5] >= self.catcher_coords[1]:
                    if not(self.item_coords[4] >= self.catcher_coords[0] and self.item_coords[4] <= self.catcher_coords[2]):
                        if canv.gettags(item)[1] == '1':
                            if not(self.catcher_coords[1] >= self.item_coords[5] and self.catcher_coords[1] <= self.item_coords[1] and ((self.catcher_coords[0] >= (self.item_coords[0] + margin) and self.catcher_coords[0] <= (self.item_coords[2] - margin)) or (self.catcher_coords[2] >= (self.item_coords[0] + margin) and self.catcher_coords[2] <= (self.item_coords[2] - margin)))):
                                continue
                        elif canv.gettags(item)[1] == '-1':
                            if not(self.catcher_coords[1] >= self.item_coords[5] and self.catcher_coords[1] <= self.item_coords[1] and ((self.catcher_coords[0] <= (self.item_coords[0] + margin) and self.catcher_coords[0] >= (self.item_coords[2] - margin)) or (self.item_coords[2] <= (self.item_coords[0] + margin) and self.catcher_coords[2] >= (self.item_coords[2] - margin)))):
                                continue
                        continue
                    canv.delete(item)
                    self.itemsOnScreen_triangle -= 1
                    if not self.__triangleDebuffApplied:
                        self.moveTime = self.triangle_moveTimeDebuff
                        self.timeToDisappear_line = self.triangle_timeToDisappear_lineDebuff
                        flicker_widget_background(widget=canv, newColor='#02041c', newColor2='black', oldColor='#02041c', frequency=200, times_to_flicker= 4)
                        self.__triangleDebuffApplied = True
                    else:
                        canv.after_cancel(self.__triangleDebuff_cancellationFunctionCallbackId)
                    
                    flicker_canvasitem_fill(itemId=rect2, newColor='black', newColor2='#02041c', oldColor='blue', frequency=200, times_to_flicker= 4)
                    self.__triangleDebuff_cancellationFunctionCallbackId = canv.after(self.triangle_debuffs_timeToDisappear, lambda:[toDefault_moveTime(), toDefault_timeToDisappear_line(), toDefault_canv_background(), toDefault_triangleDebuffApplied()])
                
            #Checking of the line elements' overlap with the catcher element is handled by the lineLoop() function.

            canv.after(self.moveTime, gameloop)

        def onClose(*args):
            curTime = datetime.now()
            curTimeStr = curTime.strftime("%m/%d/%Y | %H:%M:%S")

            match self.curDiff.get():
                case 2:#Medium difficulty
                    curDiffStr = 'Difficulty: Medium'
                case 3:#Hard difficulty
                    curDiffStr = 'Difficulty:   Hard'
                case _:#default #Easy difficulty
                    curDiffStr = 'Difficulty:   Easy'

            file1 = open("records.txt","a")
            file1.write(curTimeStr + " || " + curDiffStr + " || " + "Score: " + str(self.curScore) + '\n')
            file1.close()

            win.destroy()
            self.master.deiconify()

            self.curScore = 0
        
        def leftPress(dist):
            if canv.coords(rect2)[0] - dist >= 0:
                canv.move(rect2, -dist, 0)
            else:
                canv.moveto(rect2, 0, CONST.h - 35)

        def rightPress(dist):
            if canv.coords(rect2)[2] + dist <= CONST.w:
                canv.move(rect2, dist, 0)
            else:
                canv.moveto(rect2, CONST.w - 75, CONST.h - 35)

        def updScore(incr):
            self.curScore += incr
            curScoreStrVar.set("Score: " + str(self.curScore))

        def updLives(incr):
            self.curLives += incr
            curLivesStrVar.set("Lives: " + str(self.curLives))
            if self.curLives <= 0:
                messagebox.showwarning("Game over", "Game is over!")
                return 1
            return 0
                
        
        def newItem_regular(*args):
            x = randint(0, CONST.w - 50)
            canv.create_rectangle(x, 0, x + 50, 50, fill='red', outline='black', tags=('fall_reg'))
        
        def newItem_irregular(*args):
            x = randint(0, CONST.w - 50)
            #random speed from 0.5 to 2.0 with 0.5 as a step value
            speed = randint(1, 4)
            canv.create_rectangle(x, 0, x + 50, 50, fill='green', outline='darkgreen', tags=('fall_irreg', str(speed*0.5)))
            
        def newItem_line(*args):
            x = randint(25, CONST.w - 25)
            line = canv.create_line(x, 0, x, CONST.h, fill='#003300', tags=('line'))#, arrow='first', arrowshape=(10, 15, 15)
            flicker_canvasitem_fill(itemId=line, newColor='#003300', newColor2='#009933', oldColor='#009933', frequency=self.timeToDisappear_line/15, times_to_flicker= 5)
            for iter in range(3):
                canv.after(int(self.timeToDisappear_line/3*(iter+1)), lineLoop, line, iter)

        def newItem_triangle(*args):
            x = 0 if randint(0, 1) else CONST.w
            y = randint(0, CONST.h - 75)
            mod = -1 if x else 1 #1 if on the left side, else -1 (to draw the triangle from the right to the left or the other way)
            canv.create_polygon(x, y, x + 25*mod, y, x + 12.5*mod, y + 21.650635094611, fill='blue', tags=('triangle', str(mod)))

        def lineLoop(line, iter):
            match iter:
                case 0:
                    canv.itemconfig(line, width=2, dash=(135), fill='#009933')#, arrow='first', arrowshape=(10, 15, 13)
                    flicker_canvasitem_fill(itemId=line, newColor='#009933', newColor2='#33cc33', oldColor='#009933', frequency=self.timeToDisappear_line/24, times_to_flicker= 8)
                case 1:
                    canv.itemconfig(line, width=3, dash=(255), arrow='last', arrowshape=(10, 15, 10), fill='#33cc33')
                    flicker_canvasitem_fill(itemId=line, newColor='#33cc33', newColor2='#74de66', oldColor='#33cc33', frequency=self.timeToDisappear_line/39, times_to_flicker= 13)
                    canv.after(int(self.timeToDisappear_line/6), lambda: [canv.itemconfig(line, width=1, dash=(), fill='yellow', arrow='last', arrowshape=(10, 20, 5)), flicker_canvasitem_fill(itemId=line, newColor='yellow', newColor2='white', oldColor='yellow', frequency=self.timeToDisappear_line/120, times_to_flicker= 20)])
                case _:
                    if canv.coords(line)[0] >= canv.coords(rect2)[0] and canv.coords(line)[0] <= canv.coords(rect2)[2]:
                        updLives(self.line_livesBuff)
                        flicker_canvasitem_fill(itemId=rect2, newColor='green', newColor2='blue', oldColor='blue', frequency=200, times_to_flicker= 4)
                        flicker_widget_background(widget=curLives, newColor='green', newColor2='black', oldColor='black', frequency=200, times_to_flicker= 4)
                    canv.delete(line)
                    self.itemsOnScreen_line -= 1

        def toDefault_moveTime(*args):
            match self.curDiff.get():
                case 2: #Medium difficulty
                    self.moveTime = 10 ##milliseconds
                case 3: #Hard difficulty
                    self.moveTime = 7 ##milliseconds
                case _: #default #Easy difficulty
                    self.moveTime = 15 ##milliseconds
        
        def toDefault_timeToDisappear_line(*args):
            match self.curDiff.get():
                case 2: #Medium difficulty
                    self.timeToDisappear_line = 3000 ##milliseconds
                case 3: #Hard difficulty
                    self.timeToDisappear_line = 2000 ##milliseconds
                case _: #default #Easy difficulty
                    self.timeToDisappear_line = 3000 ##milliseconds

        def toDefault_canv_background(*args):
            canv.configure(background='black')

        def toDefault_triangleDebuffApplied(*args):
            canv.configure(background='black')
            self.__triangleDebuffApplied = False

        def flicker_canvasitem_fill(itemId, newColor, newColor2, oldColor, frequency, times_to_flicker):
            i = 1
            while i <= times_to_flicker:
                canv.after(int(frequency*(i)), lambda: canv.itemconfig(itemId, fill=newColor))
                i += 2
            i = 2
            while i <= times_to_flicker:
                canv.after(int(frequency*(i)), lambda: canv.itemconfig(itemId, fill=newColor2))
                i += 2
            canv.after(int(frequency*(times_to_flicker+1)), lambda: canv.itemconfig(itemId, fill=oldColor))
        
        def flicker_widget_background(widget, newColor, newColor2, oldColor, frequency, times_to_flicker):
            i = 1
            while i <= times_to_flicker:
                canv.after(int(frequency*(i)), lambda: widget.configure(background=newColor))
                i += 2
            i = 2
            while i <= times_to_flicker:
                canv.after(int(frequency*(i)), lambda: widget.configure(background=newColor2))
                i += 2
            canv.after(int(frequency*(times_to_flicker+1)), lambda: widget.configure(background=oldColor))

        ##MAIN CODE

        self.master.withdraw()
        win = Toplevel(self.master)
        win.resizable(0,0)
        win.protocol("WM_DELETE_WINDOW", onClose)
        win.title("Falling Nuts")
        win.wm_attributes('-alpha', '0.9')
        win.focus_force()
        
        canv = Canvas(win, width=CONST.w, height=CONST.h, background="black")
        canv.grid(sticky=(N, W, E, S))

        self.itemsOnScreen_regular = 0
        self.itemsOnScreen_irregular = 0
        self.itemsOnScreen_line = 0
        self.itemsOnScreen_triangle = 0

        match self.curDiff.get():
            case 2: #Medium difficulty
                spawnInterval = (3, 4)
                self.curLives = 5
                self.maxItems_regular = 5
                self.maxItems_irregular = 1
                self.maxItems_line = 1
                self.maxItems_triangle = 3
                self.timeToDisappear_line = 3000 ##milliseconds
                self.generationChance_line = 4 ##%percent
                self.generationChance_triangle = 2 ##%percent
                self.line_livesBuff = 3
                self.triangle_moveTimeDebuff = 16 ##milliseconds
                self.triangle_timeToDisappear_lineDebuff = 4000 ##milliseconds
                self.triangle_debuffs_timeToDisappear = 10000 ##milliseconds
                self.moveTime = 10 ##milliseconds
                for i in range(3):
                    canv.after(randint(spawnInterval[0], spawnInterval[1])*1000, newItem_regular)
                    self.itemsOnScreen_regular += 1
            case 3: #Hard difficulty
                spawnInterval = (1, 3)
                self.curLives = 3
                self.maxItems_regular = 6
                self.maxItems_irregular = 2
                self.maxItems_line = 2
                self.maxItems_triangle = 3
                self.timeToDisappear_line = 2000 ##milliseconds
                self.generationChance_line = 3 ##%percent
                self.generationChance_triangle = 3 ##%percent
                self.line_livesBuff = 3
                self.triangle_moveTimeDebuff = 11 ##milliseconds
                self.triangle_timeToDisappear_lineDebuff = 3000 ##milliseconds
                self.triangle_debuffs_timeToDisappear = 11000 ##milliseconds
                self.moveTime = 7 ##milliseconds
                for i in range(5):
                    canv.after(randint(spawnInterval[0], spawnInterval[1])*1000, newItem_regular)
                    self.itemsOnScreen_regular += 1
            case _: #default #Easy difficulty
                spawnInterval = (4, 5)
                self.curLives = 7
                self.maxItems_regular = 3
                self.maxItems_irregular = 1
                self.maxItems_line = 1
                self.maxItems_triangle = 2
                self.timeToDisappear_line = 3000 ##milliseconds
                self.generationChance_line = 4 ##%percent
                self.generationChance_triangle = 1 ##%percent
                self.line_livesBuff = 2
                self.triangle_moveTimeDebuff = 20 ##milliseconds
                self.triangle_timeToDisappear_lineDebuff = 4000 ##milliseconds
                self.triangle_debuffs_timeToDisappear = 7000 ##milliseconds
                self.moveTime = 15 ##milliseconds
                canv.after(randint(spawnInterval[0], spawnInterval[1])*1000, newItem_regular)
                self.itemsOnScreen_regular += 1

        curScoreStrVar = StringVar()
        curLivesStrVar = StringVar()
        updScore(0)
        updLives(0)
        curScore = Label(win, textvariable=curScoreStrVar, font=('Times New Roman', '20'), background='black', foreground='white')
        curLives = Label(win, textvariable=curLivesStrVar, font=('Times New Roman', '20'), background='black', foreground='white')
        curScore.place(x=10, y=10)
        curLives.place(x=10, y=45)

        x = randint(0, CONST.w - 75)
        rect2 = canv.create_rectangle(x, CONST.h - 35, x + 75, CONST.h, fill='blue', outline='darkblue')

        #https://stackoverflow.com/questions/7299955/tkinter-binding-a-function-with-arguments-to-a-widget
        #the link is about why there is uselessData variable after lambda expression
        win.bind("<KeyPress-Left>", lambda uselessData: leftPress(20))
        win.bind("<KeyPress-Right>", lambda uselessData: rightPress(20))

        win.bind("<Shift-KeyPress-Right>", lambda uselessData: rightPress(150))
        win.bind("<Shift-KeyPress-Left>", lambda uselessData: leftPress(150))

        gameloop()

    def leaderboard(self):
        def onClose(*args):
            win.destroy()
            self.master.deiconify()

        self.master.withdraw()

        if not os.path.exists("records.txt") or os.stat("records.txt").st_size == 0:#проверка, существует ли файл (1) и есть ли в нём хоть что-то для выведения (2):
            messagebox.showwarning("No written records", "There are no written records yet!")
            self.master.deiconify()
            return

        win = Toplevel(self.master)
        win.resizable(0,0)
        win.protocol("WM_DELETE_WINDOW", onClose)
        win.title("Game Records")
        win.focus_force()


        textWidget = Text(win, width = 61, height = 25)

        textWidget.tag_configure('grayBackgr_Tag', background='lightgray')
        textWidget.tag_configure('whiteBackgr_Tag', background='white')

        textWidget.tag_configure('TimeStyle_Tag', foreground='Red')
        textWidget.tag_configure('DiffStyle_General_Tag', foreground='Blue')
        textWidget.tag_configure('DiffStyle_Easy_Tag', foreground='Green')
        textWidget.tag_configure('DiffStyle_Medium_Tag', foreground='#FF6103')
        textWidget.tag_configure('DiffStyle_Hard_Tag', foreground='Crimson')
        textWidget.tag_configure('ScoreStyle_Tag', foreground='#68228B')

        scrollYWidget = ttk.Scrollbar(win, orient = 'vertical', command = textWidget.yview)
        textWidget['yscrollcommand'] = scrollYWidget.set

        textWidget.grid(column = 0, row = 0, sticky = 'nwes')
        scrollYWidget.grid(column = 1, row = 0, sticky = 'ns')

        
        file1 = open("records.txt","r")
        recordsStrArr = file1.readlines()
        file1.close()
        
        i = 0
        recsNumber = len(recordsStrArr)
        while (i < recsNumber):
            if (i % 2 == 0):
                textWidget.insert('end', recordsStrArr[i], ('grayBackgr_Tag'))
            else:
                textWidget.insert('end', recordsStrArr[i], ('whiteBackgr_Tag'))
            textWidget.tag_add('TimeStyle_Tag', str(i+1)+'.0', str(i+1)+'.10')
            textWidget.tag_add('TimeStyle_Tag', str(i+1)+'.13', str(i+1)+'.21')
            textWidget.tag_add('DiffStyle_General_Tag', str(i+1)+'.25', str(i+1)+'.36')
            match textWidget.get(str(i+1)+'.36', str(i+1)+'.43'):
                case ' Medium':
                    textWidget.tag_add('DiffStyle_Medium_Tag', str(i+1)+'.36', str(i+1)+'.43')
                case '   Hard':
                    textWidget.tag_add('DiffStyle_Hard_Tag', str(i+1)+'.36', str(i+1)+'.43')
                case _:
                    textWidget.tag_add('DiffStyle_Easy_Tag', str(i+1)+'.36', str(i+1)+'.43')
            textWidget.tag_add('ScoreStyle_Tag', str(i+1)+'.46', str(i+1)+'.55')
            i += 1

        textWidget['state'] = 'disabled'#Выключает возможность добавлять новый текст
        
    def inquiry(self):
        def onClose(*args):
            win.destroy()
            self.master.deiconify()

        self.master.withdraw()
        win = Toplevel(self.master)
        win.resizable(0,0)
        win.protocol("WM_DELETE_WINDOW", onClose)
        win.title("Inquiry")
        win.focus_force()

        textWidget = Text(win, width = 140, height = 25)

        scrollYWidget = ttk.Scrollbar(win, orient = 'vertical', command = textWidget.yview)
        textWidget['yscrollcommand'] = scrollYWidget.set

        textWidget.grid(column = 0, row = 0, sticky = 'nwes')
        scrollYWidget.grid(column = 1, row = 0, sticky = 'ns')

        file1 = open("guide.txt", encoding='utf-8',mode="r")
        guideStrArr = file1.readlines()
        file1.close()

        i = 0
        recsNumber = len(guideStrArr)
        while (i < recsNumber):
            textWidget.insert('end', guideStrArr[i])
            i += 1

        textWidget['state'] = 'disabled'#Выключает возможность добавлять новый текст
        
def main():
    root = Tk()
    app = MainMenu()
    root.mainloop()  

if __name__ == '__main__':
    main()