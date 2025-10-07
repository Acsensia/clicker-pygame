# Example file showing a basic pygame "game loop"
import pygame, os
from random import randint
def testCallback(*args):
    print(args)

class CenteredElement:
    def __init__(self, x = 0, y = 0, width = 0, height = 0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
    def center_self_x(self, parentWidth):
        self.x = (parentWidth - self.width)/2
    def center_self_y(self, parentHeight):
        self.y = (parentHeight - self.height)/2
    def center_self(self, parentWidth, parentHeight):
        self.center_self_x(parentWidth)
        self.center_self_y(parentHeight)
    def arrange_group_y(self, allowed_height, y_offset, mode, group):
        elementCount = 0
        elementsCollectiveHeight = 0
        y_delta = 0
        for element in group:
            elementsCollectiveHeight += element.height
            elementCount+=1
        match mode:
            case 'margin_elements+borders':
                y_delta = (allowed_height - elementsCollectiveHeight)/(elementCount + 1)
                for element in group:
                    element.y = y_offset + y_delta
                    y_offset = element.y + element.height
            case 'margin_elements':
                y_delta = (allowed_height - elementsCollectiveHeight)/(elementCount - 1)
                group[0].y = y_offset
                y_offset = group[0].y + group[0].height
                iter = 1
                while iter < elementCount:
                    group[iter].y = y_offset + y_delta
                    y_offset = group[iter].y + group[iter].height
                    iter+=1
            case 'margin_elements+bordersDown':
                y_delta = (allowed_height - elementsCollectiveHeight)/(elementCount)
                group[0].y = y_offset
                y_offset = group[0].y + group[0].height
                iter = 1
                while iter < elementCount:
                    group[iter].y = y_offset + y_delta
                    y_offset = group[iter].y + group[iter].height
                    iter+=1
            case 'margin_elements+bordersUp':
                y_delta = (allowed_height - elementsCollectiveHeight)/(elementCount)
                for element in group:
                    element.y = y_offset + y_delta
                    y_offset = element.y + element.height
    def drawRectWithAlpha(self, coordinatesTuple, sizeTuple, color_rgba, surface):
        background = pygame.Surface((sizeTuple))
        background.set_alpha(color_rgba[3])
        background.fill(color_rgba)#possible error cause RGBA
        return surface.blit(background, coordinatesTuple)#return just in case

class Label(pygame.Rect, CenteredElement):
    def __init__(self, width, height, x, y, font, text, color_Text, surface, alignMode, color_background=(0, 0, 0, 0)):
        super().__init__(x, y, width, height)
        self.font = font
        self.text = text
        self.color_Text = color_Text
        self.surface = surface
        self.alignMode = alignMode
        self.color_background = color_background
        self.updateValues()

    def updateValues(self):
        self.textImageSize = self.font.size(self.text)
        match self.alignMode:
            case 'Left':
                self.textCoords = (self.x, (self.height - self.textImageSize[1])/2 + self.y)
            case 'Center':
                self.textCoords = ((self.width - self.textImageSize[0])/2 + self.x, (self.height - self.textImageSize[1])/2 + self.y)
            case 'Right':
                self.textCoords = (self.width - self.textImageSize[0] + self.x, (self.height - self.textImageSize[1])/2 + self.y)
            case _:
                self.textCoords = (self.x, self.y)
                print("Неправильно введён Label.alignMode: " + self.alignMode)

    def draw(self):
        self.updateValues()
        textImage = self.font.render(self.text, True, self.color_Text)
        self.drawRectWithAlpha((self.textCoords[0]-3, self.textCoords[1]), (self.textImageSize[0]+3, self.textImageSize[1]), self.color_background, self.surface)
        self.surface.blit(textImage, self.textCoords)

class FloatingLabel(Label):
    def __init__(self, width, height, x, y, font, text, color_Text, surface, labelwidth_offset = 15, labely_offset = -15, color_background=(0, 0, 0, 0)):
        super().__init__(width=width, height=height, x=x, y=y, font=font, text=text, color_Text=color_Text, surface=surface, alignMode='Left', color_background=color_background)
        self.labelwidth_offset = labelwidth_offset
        self.labely_offset = labely_offset
        self.updatePositioning(pygame.mouse.get_pos())
        """self.labelx_multiplier = 1
        surfaceWidthHalf = surface.get_width()/2
        if x+width > surfaceWidthHalf:
            self.alignMode = 'Right'
            self.labelwidth_offset *= -1
            self.labelx_multiplier = 0"""
    def updatePositioning(self, mouse_pos):
        self.labelx_multiplier = 1
        if self.labelwidth_offset < 0:
            self.labelwidth_offset *= -1
        self.alignMode = 'Left'
        surfaceWidthHalf = self.surface.get_width()/2
        if mouse_pos[0] > surfaceWidthHalf:
            self.alignMode = 'Right'
            self.labelwidth_offset *= -1
            self.labelx_multiplier = 0
    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        self.updatePositioning(mouse_pos)
        self.width = mouse_pos[0] + self.labelwidth_offset
        self.x = mouse_pos[0]*self.labelx_multiplier + self.labelwidth_offset*(0 if self.alignMode == 'Right' else 1)
        self.y = mouse_pos[1] + self.labely_offset
        super().draw()

class Button(pygame.Rect, CenteredElement):
    def __init__(self, width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, sizeIncrease_Hover = 7, sizeIncrease_MouseButon_Down = 4, state_Active = True, state_FullyDisabled = False, color_Inactive = (0, 0, 0, 150)):
        super().__init__(x, y, width, height)

        self.color = color
        self.color_Hover = color_Hover
        self.color_MouseButton_Down = color_MouseButton_Down
        self.surface = surface
        self.callback = callback
        self.state_Active = state_Active
        self.state_FullyDisabled = state_FullyDisabled
        self.color_Inactive = color_Inactive
        self.sizeIncrease_Hover = sizeIncrease_Hover
        self.sizeIncrease_MouseButon_Down = sizeIncrease_MouseButon_Down
    def draw(self, color, rect):
        pygame.draw.rect(self.surface, color, rect)

    def __initState_mouseButtonUp__(self):
        self.callback()
    def __initState_mouseButtonDown__(self):
        self.draw(self.color_MouseButton_Down, self.inflate(self.sizeIncrease_MouseButon_Down, self.sizeIncrease_MouseButon_Down))
    def __initState_mouseHoverNoStates__(self):
        self.draw(self.color_Hover, self.inflate(self.sizeIncrease_Hover, self.sizeIncrease_Hover))
    def __initState_mouseHover__(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        return 1
    def __initState_default__(self):
        self.draw(self.color, self)
    def __initState_inactive__(self):
        self.draw(self.color_Inactive, self)
    def __initState_mouseHover_inactive__(self):
        self.__initState_inactive__()
    def __initState_fullyDisabled__(self):
        pass#intentionally
    def update(self, mouseButton_Up=False):
        if not self.state_FullyDisabled:
            if self.state_Active:
                if self.collidepoint(pygame.mouse.get_pos()):
                    if (mouseButton_Up):
                        self.__initState_mouseButtonUp__()
                    if (pygame.mouse.get_pressed()[0]):
                        self.__initState_mouseButtonDown__()
                    else:
                        self.__initState_mouseHoverNoStates__()
                    return self.__initState_mouseHover__()
                else:
                    return self.__initState_default__()
            else:
                if self.collidepoint(pygame.mouse.get_pos()):
                    return self.__initState_mouseHover_inactive__()
                else:
                    return self.__initState_inactive__()
        else:
            return self.__initState_fullyDisabled__()

class TextButton(Button):
        def __init__(self, width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, font, text, color_Text, color_Text_Hover, color_Text_MouseButton_Down, sizeIncrease_Hover = 7, sizeIncrease_MouseButon_Down = 4, color_Text_Inactive = 'white', state_Active = True, state_FullyDisabled = False, color_Inactive = (0, 0, 0, 150)):
            super().__init__(width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, sizeIncrease_Hover, sizeIncrease_MouseButon_Down, state_Active, state_FullyDisabled, color_Inactive,)

            self.font = font
            self.text = text
            self.color_Text = color_Text
            self.color_Text_Hover = color_Text_Hover
            self.color_Text_MouseButton_Down = color_Text_MouseButton_Down
            self.color_Text_Inactive = color_Text_Inactive
        def draw(self, color, textColor, rect):
            super().draw(color, rect)

            textImage = self.font.render(self.text, True, textColor)
            textImageSize = self.font.size(self.text)
            self.surface.blit(textImage, ((rect.width - textImageSize[0])/2 + rect.x, (rect.height - textImageSize[1])/2 + rect.y + 3))
        def __initState_mouseButtonUp__(self):
            self.callback()
        def __initState_mouseButtonDown__(self):
            self.draw(self.color_MouseButton_Down, self.color_Text_MouseButton_Down, self.inflate(self.sizeIncrease_MouseButon_Down, self.sizeIncrease_MouseButon_Down))
        def __initState_mouseHoverNoStates__(self):
            self.draw(self.color_Hover, self.color_Text_Hover, self.inflate(self.sizeIncrease_Hover, self.sizeIncrease_Hover))
        def __initState_default__(self):
            self.draw(self.color, self.color_Text, self)
        def __initState_inactive__(self):
            self.draw(self.color, self.color_Text_Inactive, self)
            self.drawRectWithAlpha((self.x, self.y), (self.width, self.height), self.color_Inactive, self.surface)

class Image(pygame.Rect, CenteredElement):
    def __init__(self, width, height, x, y, surface, path):
        super().__init__(x, y, width, height)

        self.surface = surface
        self.path = path
    
    def draw(self):
        image = pygame.image.load(self.path)
        image = pygame.transform.scale(image, (self.width, self.height))
        self.surface.blit(image, (self.x, self.y))

class ImageButton(Button):
    def __init__(self, width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, imagePath, imageCoverArea, sizeIncrease_Hover = 7, sizeIncrease_MouseButon_Down = 4, state_Active = True, state_FullyDisabled = False, color_Inactive = (0, 0, 0, 150)):
        super().__init__(width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, sizeIncrease_Hover, sizeIncrease_MouseButon_Down, state_Active, state_FullyDisabled, color_Inactive)

        self.imageCoverArea = imageCoverArea
        self.image = Image(width=self.width*imageCoverArea, height=self.height*imageCoverArea, x=self.x, y=self.y, surface=self.surface, path=imagePath)
    def __initState_mouseButtonUp__(self):
        self.callback()
    def __initState_mouseButtonDown__(self):
        temp_inflatedSelf = self.inflate(self.sizeIncrease_MouseButon_Down, self.sizeIncrease_MouseButon_Down)
        self.draw(self.color_MouseButton_Down, temp_inflatedSelf)
        self.__drawScaledImage__(temp_inflatedSelf)
    def __initState_mouseHoverNoStates__(self):
        temp_inflatedSelf = self.inflate(self.sizeIncrease_Hover, self.sizeIncrease_Hover)
        self.draw(self.color_Hover, temp_inflatedSelf)
        self.__drawScaledImage__(temp_inflatedSelf)
    def __initState_default__(self):
        self.draw(self.color, self)
        self.image.draw()
    def __initState_inactive__(self):
        self.draw(self.color, self)
        self.image.draw()
        self.drawRectWithAlpha((self.x, self.y), (self.width, self.height), self.color_Inactive, self.surface)
    def update(self, mouseButton_Up=False):
        temp_for_return = super().update(mouseButton_Up)
        self.updImageCoordinates()
        return temp_for_return
    def updImageCoordinates(self):
        self.image.center_self(self.width, self.height)
        self.image.x += self.x
        self.image.y += self.y
    def __drawScaledImage__(self, rect):
        temp_transformedImage = pygame.transform.scale(pygame.image.load(self.image.path), (rect[2]*self.imageCoverArea, rect[3]*self.imageCoverArea))
        self.image.surface.blit(temp_transformedImage, (rect[0], rect[1]))

class ImageButton_FloatingText(ImageButton):
    def __init__(self, width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, imagePath, imageCoverArea, font, text, color_Text, font_Inactive, text_Inactive, color_Text_Inactive, color_Text_Background_Inactive, sizeIncrease_Hover = 7, sizeIncrease_MouseButon_Down = 4, color_Text_Background=(0, 0, 0, 0), state_Active = True, state_FullyDisabled = False, color_Inactive = (0, 0, 0, 150), drawFloatingTextRightAway = True):
        super().__init__(width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, imagePath, imageCoverArea, sizeIncrease_Hover, sizeIncrease_MouseButon_Down, state_Active, state_FullyDisabled, color_Inactive)
        
        self.drawFloatingTextRightAway = drawFloatingTextRightAway
        self.labels = []
        self.labels_Inactive = []
        iter = 0
        for string in text:
            temp_labely_offset = -15 if iter == 0 else -15 + self.labels[iter-1].textImageSize[1]
            self.labels.append(FloatingLabel(width=width, height=1, x=x, y=y, font=font, text=string, color_Text=color_Text, surface=surface, color_background=color_Text_Background, labely_offset=temp_labely_offset))
            iter += 1
        iter = 0
        for string in text_Inactive:
            temp_labely_offset = -15 if iter == 0 else -15 + self.labels_Inactive[iter-1].textImageSize[1]
            self.labels_Inactive.append(FloatingLabel(width=width, height=1, x=x, y=y, font=font_Inactive, text=string, color_Text=color_Text_Inactive, surface=surface, color_background=color_Text_Background_Inactive, labely_offset=temp_labely_offset))
            iter += 1
        #self.label = FloatingLabel(width=width, height=1, x=x, y=y, font=font, text=text, color_Text=color_Text, surface=surface, color_background=color_Text_Background)
        #self.label_Inactive = FloatingLabel(width=width, height=1, x=x, y=y, font=font_Inactive, text=string, color_Text=color_Text_Inactive, surface=surface, color_background=color_Text_Background_Inactive)

    def __initState_mouseHover__(self):
        super().__initState_mouseHover__()
        if self.drawFloatingTextRightAway:
            #self.label.draw()
            for label in self.labels:
                label.draw()
        return 1
    def __initState_mouseHover_inactive__(self):
        super().__initState_inactive__()
        if self.drawFloatingTextRightAway:
            #self.label_Inactive.draw()
            for label in self.labels_Inactive:
                label.draw()
        return 2
    

class RotationImage(Image):
    def __init__(self, width, height, x, y, surface, path):
        super().__init__(width, height, x, y, surface, path)

    def draw(self, rotationAngle):
        image = pygame.image.load(self.path)
        image = pygame.transform.scale(image, (self.width, self.height))
        image = pygame.transform.rotate(image, rotationAngle)

        imageRect = image.get_rect()
        old_x = self.x
        old_y = self.y
        self.x -= imageRect.width/2 - self.width/2
        self.y -= imageRect.height/2 - self.height/2
        self.surface.blit(image, (self.x, self.y))
        self.x = old_x
        self.y = old_y


class Game:
    class clickprojectile(Image):
        def __init__(self, width, height, surface, bottomRect, array, impulse, x, y, path):
            super().__init__(width=width, height=height, x=x, y=y, surface=surface, path = path)

            self.impulse = impulse
            self.bottomRect = bottomRect
            self.array = array
            self.array.append(self)
            self.x = randint(self.x - 50, self.x + 50)
            self.y = randint(self.y - 50, self.y + 50)
        def update(self):
            self.y += self.impulse
            if self.colliderect(self.bottomRect):
                self.array.remove(self)
            else:
                self.impulse += 1
            self.draw()
    class checkerboard(pygame.Rect, CenteredElement):
        def __init__(self, width, height, x, y, rows, columns, surface, imagePath, callback, callbackArgumentOffset, color, color_Hover, color_MouseButton_Down, color_Inactive, font, text, color_Text, color_Text_Background, font_Inactive, text_Inactive, color_Text_Inactive, color_Text_Background_Inactive):
            super().__init__(x, y, width, height)

            self.rows = rows
            self.columns = columns
            self.surface = surface
            self.array = []
            self.image = Image(width, height, x, y, surface, imagePath)
            self.callback = callback
            self.callbackArgumentOffset = callbackArgumentOffset
            self.color = color
            self.color_Hover = color_Hover
            self.color_MouseButton_Down = color_MouseButton_Down
            self.color_Inactive = color_Inactive
            self.font = font
            self.text = text
            self.color_Text = color_Text
            self.color_Text_Background = color_Text_Background
            self.font_Inactive = font_Inactive
            self.text_Inactive = text_Inactive
            self.color_Text_Inactive = color_Text_Inactive
            self.color_Text_Background_Inactive = color_Text_Background_Inactive
            self.updateValues()
        def updateValues(self):
            def createSpecificLambda(func, *args):
                return lambda: func(args[0] + args[1]*args[2] + args[3])
            self.image = Image(self.width, self.height, self.x, self.y, self.surface, self.image.path)
            self.array.clear()
            imageButtonwidth = self.width/self.columns
            imageButtonheight = self.height/self.rows
            iter_row = 0
            while iter_row < self.rows:
                iter_column = 0
                while iter_column < self.columns:
                    temp_Lambda = createSpecificLambda(self.callback, self.callbackArgumentOffset, iter_row, self.columns, iter_column)
                    self.array.append(ImageButton_FloatingText(width=imageButtonwidth, height=imageButtonheight, x=self.x+imageButtonwidth*iter_column, y=self.y+imageButtonheight*iter_row, color=self.color, color_Hover=self.color_Hover, color_MouseButton_Down=self.color_MouseButton_Down, surface=self.surface, callback=temp_Lambda, imagePath=self.image.path, imageCoverArea=1, font=self.font, text=self.text[iter_row*self.columns + iter_column], color_Text=self.color_Text, font_Inactive=self.font_Inactive, text_Inactive=self.text_Inactive[iter_row*self.columns + iter_column], color_Text_Inactive=self.color_Text_Inactive, color_Text_Background_Inactive=self.color_Text_Background_Inactive, sizeIncrease_Hover=0, sizeIncrease_MouseButon_Down=0, color_Text_Background=self.color_Text_Background, drawFloatingTextRightAway=False, color_Inactive=self.color_Inactive))
                    iter_column += 1
                iter_row += 1

        def update(self, mouseButton_Up=False):
            self.image.draw()
            buttonsUpdateResults = []
            for imageButton in self.array:
                buttonsUpdateResults.append(imageButton.update(mouseButton_Up))
            return buttonsUpdateResults
    class shopItem(Button):
        def __init__(self, width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, color_demonstration_small, color_demonstration_middle, color_demonstration_big, font_name, name, color_name, color_name_hover, color_name_mousebutton_down, font_price, price, color_price, color_price_hover, color_price_mousebutton_down, price_imagePath, id, show_price = True, sizeIncrease_Hover = 7, sizeIncrease_MouseButon_Down = 4, state_Active = True, state_FullyDisabled = False, color_Inactive = (0, 0, 0, 150)):
            super().__init__(width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, sizeIncrease_Hover, sizeIncrease_MouseButon_Down, state_Active, state_FullyDisabled, color_Inactive)
            self.color_demonstration_small = color_demonstration_small
            self.color_demonstration_middle = color_demonstration_middle
            self.color_demonstration_big = color_demonstration_big
            self.font_name = font_name
            self.name = name
            self.color_name = color_name
            self.color_name_hover = color_name_hover#
            self.color_name_mousebutton_down = color_name_mousebutton_down#
            self.font_price = font_price
            self.price = price
            self.color_price = color_price
            self.color_price_hover = color_price_hover
            self.color_price_mousebutton_down = color_price_mousebutton_down
            self.price_imagePath = price_imagePath
            self.id = id
            self.show_price = show_price
        def draw(self, color, nameColor, priceColor, rect):
            super().draw(color, rect)
            demonstration_bigRect = pygame.draw.rect(self.surface, self.color_demonstration_big, (self.x + 7, self.y + 7, self.height - 14, self.height - 14))
            demonstration_midRect = pygame.draw.rect(self.surface, self.color_demonstration_middle, (demonstration_bigRect[0] + demonstration_bigRect[2]*1/4, demonstration_bigRect[1] + demonstration_bigRect[3]*1/4, demonstration_bigRect[2]*3/4, demonstration_bigRect[3]*3/4))
            demonstration_smlRect = pygame.draw.rect(self.surface, self.color_demonstration_small, (demonstration_midRect[0] + demonstration_midRect[2]*1/4, demonstration_midRect[1] + demonstration_midRect[3]*1/4, demonstration_midRect[2]*3/4, demonstration_midRect[3]*3/4))

            temp_nameLabelx = demonstration_bigRect[0]+demonstration_bigRect.width+7
            nameLabel = Label(x=temp_nameLabelx, y=demonstration_bigRect[1], width=self.width-temp_nameLabelx-7+self.x, height=(self.height - 14)/4, font=self.font_name, text=self.name, color_Text=nameColor, surface=self.surface, alignMode="Left")
            priceLabel = Label(x=nameLabel.x, y=nameLabel.y + nameLabel.height + 21, width=nameLabel.width, height=nameLabel.height, font=self.font_price, text=self.price, color_Text=priceColor, surface=self.surface, alignMode="Left")
            priceImage = Image(width=priceLabel.textImageSize[1], height=priceLabel.textImageSize[1], x=priceLabel.textCoords[0]+priceLabel.textImageSize[0]+7, y=priceLabel.textCoords[1], surface=self.surface, path=self.price_imagePath)
            nameLabel.draw()
            if self.show_price:
                priceLabel.draw()
                priceImage.draw()
        def __initState_mouseButtonDown__(self):
            self.draw(color=self.color_MouseButton_Down, nameColor=self.color_name_mousebutton_down, priceColor=self.color_price_mousebutton_down, rect=self.inflate(self.sizeIncrease_MouseButon_Down, self.sizeIncrease_MouseButon_Down))
        def __initState_mouseHoverNoStates__(self):
            self.draw(color=self.color_Hover, nameColor=self.color_name_hover, priceColor=self.color_price_hover, rect=self.inflate(self.sizeIncrease_Hover, self.sizeIncrease_Hover))
        def __initState_default__(self):
            self.draw(color=self.color, nameColor=self.color_name, priceColor=self.color_price, rect=self)
        def __initState_inactive__(self):#maybe todo: inactive name and price colors?
            self.draw(color=self.color, nameColor=self.color_name, priceColor=self.color_price, rect=self)
            self.drawRectWithAlpha((self.x, self.y), (self.width, self.height), self.color_Inactive, self.surface)
    class ImageButton_FloatingAndCorneredTexts(ImageButton_FloatingText):
        def __init__(self, width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, imagePath, imageCoverArea, font, text, color_Text, font_Inactive, text_Inactive, color_Text_Inactive, color_Text_Background_Inactive, corneredText, color_CorneredText, color_CorneredText_Background, font_CorneredText, corneredTextMode = 'SouthEast', sizeIncrease_Hover = 7, sizeIncrease_MouseButon_Down = 4, color_Text_Background=(0, 0, 0, 0), state_Active = True, state_FullyDisabled = False, color_Inactive = (0, 0, 0, 150), drawFloatingTextRightAway = True):
            super().__init__(width, height, x, y, color, color_Hover, color_MouseButton_Down, surface, callback, imagePath, imageCoverArea, font, text, color_Text, font_Inactive, text_Inactive, color_Text_Inactive, color_Text_Background_Inactive, sizeIncrease_Hover, sizeIncrease_MouseButon_Down, color_Text_Background, state_Active, state_FullyDisabled, color_Inactive, drawFloatingTextRightAway)
            self.corneredText = corneredText
            self.color_CorneredText = color_CorneredText
            self.color_CorneredText_Background = color_CorneredText_Background
            self.font_CorneredText = font_CorneredText
            self.corneredTextMode = corneredTextMode
            self.updateValues()
        def updateValues(self):
            self.corneredLabel = Label(width=self.width, height=1, x=self.x, y=self.y, font=self.font_CorneredText, text=self.corneredText, color_Text=self.color_CorneredText, surface=self.surface, alignMode='Left', color_background=self.color_CorneredText_Background)
            match self.corneredTextMode:
                case 'NorthEast':
                    self.corneredLabel.x = self.x
                    self.corneredLabel.y = self.y - self.corneredLabel.textImageSize[1]
                    self.corneredLabel.height = self.corneredLabel.textImageSize[1]
                    self.corneredLabel.alignMode = 'Right'
                case 'SouthEast':
                    self.corneredLabel.x = self.x
                    self.corneredLabel.y = self.y + self.height - self.corneredLabel.textImageSize[1]
                    self.corneredLabel.height = self.corneredLabel.textImageSize[1]
                    self.corneredLabel.alignMode = 'Right'
                case 'SouthWest':
                    self.corneredLabel.x += 3
                    self.corneredLabel.y = self.y + self.height - self.corneredLabel.textImageSize[1]
                    self.corneredLabel.height = self.corneredLabel.textImageSize[1]
                case 'NorthWest':
                    self.corneredLabel.x += 3
                    self.corneredLabel.y = self.y - self.corneredLabel.textImageSize[1]
                    self.corneredLabel.height = self.corneredLabel.textImageSize[1]
        def __initState_mouseButtonDown__(self):
            super().__initState_mouseButtonDown__()
            self.corneredLabel.draw()
        def __initState_mouseHover__(self):
            self.corneredLabel.draw()
            return super().__initState_mouseHover__()
        def __initState_default__(self):
            super().__initState_default__()
            self.corneredLabel.draw()
        def __initState_inactive__(self):
            super().__initState_inactive__()
            self.corneredLabel.draw()
        def __initState_mouseHover_inactive__(self):
            self.corneredLabel.draw()
            Button.__initState_mouseHover_inactive__(self)
            if self.drawFloatingTextRightAway:
                for label in self.labels_Inactive:
                    label.draw()
            return 2
    class Theme():
        def __init__(self, name = 'Default', id = 0, price = '0', background = '#A0A0A0', upperBarColor = '#606060', sideBarColor = '#404040', lowerBarColor = '#606060', buttonColor = '#606060', buttonColor_Hover = '#404040', buttonColor_MouseButton_Down = '#202020', buttonColor_Inactive = (0, 0, 0, 150), buttonTextColor = '#000000', buttonTextColor_Hover = '#A8A8A8', buttonTextColor_MouseButton_Down = '#FFFFFF', buttonTextColor_Inactive = '#909090', buttonTextFont = ('Grand9KPixel.ttf', 62), labelColor = '#000000', labelFont = ('Grand9KPixel.ttf', 52), gameWindowLabelColor_Coin = (204, 204, 0), gameWindowLabelFont_Coin = ('Grand9KPixel.ttf', 40), gameWindowLabelColor_Diamond = (0, 255, 255), gameWindowLabelFont_Diamond = ('Grand9KPixel.ttf', 40), floatingLabel_Color = '#000000', floatingLabel_Color_Inactive = '#660000', floatingLabel_Background = (255, 255, 255, 150), floatingLabel_Background_Inactive = (255, 255, 255, 150), floatingLabel_Font = ('Grand9KPixel.ttf', 15), floatingLabel_Font_Inactive = ('Grand9KPixel.ttf', 15), shopItem_nameColor = '#000000', shopItem_nameColor_Hover = '#A8A8A8', shopItem_nameColor_MouseButton_Down = '#FFFFFF', shopItem_nameFont = ('Grand9KPixel.ttf', 40), shopItem_priceColor = '#00A5A5', shopItem_priceColor_Hover = '#00CCCC', shopItem_priceColor_MouseButton_Down = '#00AAAA', shopItem_priceFont = ('Grand9KPixel.ttf', 30), corneredTextColor = '#000000', corneredTextColor_Background = (255, 255, 255, 155), corneredText_Font = ('Grand9KPixel.ttf', 15)):
            self.name = name
            self.id = id
            self.price = price
            self.background = background
            self.upperBarColor = upperBarColor
            self.sideBarColor = sideBarColor
            self.lowerBarColor = lowerBarColor
            self.buttonColor = buttonColor
            self.buttonColor_Hover = buttonColor_Hover
            self.buttonColor_MouseButton_Down = buttonColor_MouseButton_Down
            self.buttonColor_Inactive = buttonColor_Inactive
            self.buttonTextColor = buttonTextColor
            self.buttonTextColor_Hover = buttonTextColor_Hover
            self.buttonTextColor_MouseButton_Down = buttonTextColor_MouseButton_Down
            self.buttonTextColor_Inactive = buttonTextColor_Inactive
            self.buttonTextFont = pygame.font.Font(buttonTextFont[0], buttonTextFont[1])#potential error if changed after initialization
            self.labelColor = labelColor
            self.labelFont = pygame.font.Font(labelFont[0], labelFont[1])#potential error if changed after initialization
            self.gameWindowLabelColor_Coin = gameWindowLabelColor_Coin
            self.gameWindowLabelFont_Coin = pygame.font.Font(gameWindowLabelFont_Coin[0], gameWindowLabelFont_Coin[1])
            self.gameWindowLabelColor_Diamond = gameWindowLabelColor_Diamond
            self.gameWindowLabelFont_Diamond = pygame.font.Font(gameWindowLabelFont_Diamond[0], gameWindowLabelFont_Diamond[1])
            self.floatingLabel_Color = floatingLabel_Color
            self.floatingLabel_Color_Inactive = floatingLabel_Color_Inactive
            self.floatingLabel_Background = floatingLabel_Background
            self.floatingLabel_Background_Inactive = floatingLabel_Background_Inactive
            self.floatingLabel_Font = pygame.font.Font(floatingLabel_Font[0], floatingLabel_Font[1])#potential error if changed after initialization
            self.floatingLabel_Font_Inactive = pygame.font.Font(floatingLabel_Font_Inactive[0], floatingLabel_Font_Inactive[1])#potential error if changed after initialization
            self.shopItem_nameColor = shopItem_nameColor
            self.shopItem_nameColor_Hover = shopItem_nameColor_Hover
            self.shopItem_nameColor_MouseButton_Down = shopItem_nameColor_MouseButton_Down
            self.shopItem_nameFont = pygame.font.Font(shopItem_nameFont[0], shopItem_nameFont[1])
            self.shopItem_priceColor = shopItem_priceColor
            self.shopItem_priceColor_Hover = shopItem_priceColor_Hover
            self.shopItem_priceColor_MouseButton_Down = shopItem_priceColor_MouseButton_Down
            self.shopItem_priceFont = pygame.font.Font(shopItem_priceFont[0], shopItem_priceFont[1])#potential error if changed after initialization
            self.corneredTextColor = corneredTextColor
            self.corneredTextColor_Background = corneredTextColor_Background
            self.corneredText_Font = pygame.font.Font(corneredText_Font[0], corneredText_Font[1])

    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.__checkRecordsFileExistance__()
        self.recordsFile = open("records.txt", "r+")

        #THEMES
        self.theme_default = Game.Theme()
        self.theme = self.theme_default
        self.shopThemes = [
            Game.Theme(
                name="Bloody Hell",
                id=1,
                price='10',
                background='#ff3330',
                upperBarColor='#bf2b20',
                sideBarColor='#b0271e',
                lowerBarColor='#bf2b20',
                buttonColor='#8f2018',
                buttonColor_Hover='#701913',
                buttonColor_MouseButton_Down='#59140f',
                buttonColor_Inactive=(0, 0, 0, 150),
                buttonTextColor='#FFFFFF',
                buttonTextColor_Hover='#A8A8A8',
                buttonTextColor_MouseButton_Down='#000000',
                buttonTextColor_Inactive='#909090',
                labelColor='#FFFFFF',
                labelFont=('Grand9KPixel.ttf', 52),
                gameWindowLabelColor_Coin=(204, 204, 0),
                gameWindowLabelColor_Diamond=(0, 255, 255),
                floatingLabel_Color='#FFFFFF',
                floatingLabel_Color_Inactive='#AAAA00',
                floatingLabel_Background=(0, 0, 0, 150),
                floatingLabel_Background_Inactive=(0, 0, 0, 150),
                shopItem_nameColor='#FFFFFF',
                shopItem_nameColor_Hover='#A8A8A8',
                shopItem_nameColor_MouseButton_Down='#000000',
                shopItem_priceColor='#00A5A5',
                shopItem_priceColor_Hover='#00CCCC',
                shopItem_priceColor_MouseButton_Down='#00AAAA',
                corneredTextColor='#000000',
                corneredTextColor_Background=(255, 255, 255, 155),
                ),
            Game.Theme(
                name="Vegan Mood",
                id=2,
                price='20',
                background='#7eff22',
                upperBarColor='#67d11c',
                sideBarColor='#5dbd19',
                lowerBarColor='#67d11c',
                buttonColor='#55ab17',
                buttonColor_Hover='#499414',
                buttonColor_MouseButton_Down='#3c7a10',
                buttonColor_Inactive=(0, 0, 0, 150),
                buttonTextColor='#FFFFFF',
                buttonTextColor_Hover='#A8A8A8',
                buttonTextColor_MouseButton_Down='#e8e3e0',
                buttonTextColor_Inactive='#909090',
                labelColor='#FFFFFF',
                gameWindowLabelColor_Coin=(204, 204, 0),
                gameWindowLabelColor_Diamond=(0, 255, 255),
                floatingLabel_Color='#FFFFFF',
                floatingLabel_Color_Inactive='#AAAA00',
                floatingLabel_Background=(0, 0, 0, 200),
                floatingLabel_Background_Inactive=(0, 0, 0, 200),
                shopItem_nameColor='#FFFFFF',
                shopItem_nameColor_Hover='#A8A8A8',
                shopItem_nameColor_MouseButton_Down='#e8e3e0',
                shopItem_priceColor='#00A5A5',
                shopItem_priceColor_Hover='#00CCCC',
                shopItem_priceColor_MouseButton_Down='#00AAAA',
                corneredTextColor='#000000',
                corneredTextColor_Background=(255, 255, 255, 155),
                ),
            Game.Theme(
                name="Gay Blue",
                id=3,
                price='30',
                background='#45fcff',
                upperBarColor='#3bc9c7',
                sideBarColor='#2b8a85',
                lowerBarColor='#3bc9c7',
                buttonColor='#30a3a1',
                buttonColor_Hover='#2b918f',
                buttonColor_MouseButton_Down='#268280',
                buttonColor_Inactive=(0, 0, 0, 150),
                buttonTextColor='#FFFFFF',
                buttonTextColor_Hover='#A8A8A8',
                buttonTextColor_MouseButton_Down='#e8e3e0',
                buttonTextColor_Inactive='#909090',
                labelColor='#FFFFFF',
                gameWindowLabelColor_Coin=(204, 204, 0),
                gameWindowLabelColor_Diamond=(255, 255, 255),
                floatingLabel_Color='#FFFFFF',
                floatingLabel_Color_Inactive='#AAAA00',
                floatingLabel_Background=(0, 0, 0, 200),
                floatingLabel_Background_Inactive=(0, 0, 0, 200),
                shopItem_nameColor='#FFFFFF',
                shopItem_nameColor_Hover='#A8A8A8',
                shopItem_nameColor_MouseButton_Down='#e8e3e0',
                shopItem_priceColor='#FFFFFF',
                shopItem_priceColor_Hover='#A8A8A8',
                shopItem_priceColor_MouseButton_Down='#e8e3e0',
                corneredTextColor='#000000',
                corneredTextColor_Background=(255, 255, 255, 155),
                ),
        ]
        
        #DIFFICULTIES
        self.curDifficulty = 0
        self.curRecords = []
        self.__getInfoFromRecordsFile__()
        self.difficulties = (
            [
                [-10, -10, 0.2, self.curRecords[2]],
                [-20, -20, 0.2, self.curRecords[3]],
                [-30, -30, 0.2, self.curRecords[4]],
                [-40, -40, 0.2, self.curRecords[5]],

                [-50, -50, 0.2, self.curRecords[6]],
                [-60, -60, 0.2, self.curRecords[7]],
                [-70, -70, 0.2, self.curRecords[8]],
                [-80, -80, 0.2, self.curRecords[9]],

                [-10, 0, 0, self.curRecords[10]],
                [-20, 0, 0, self.curRecords[11]],
                [-30, 0, 0, self.curRecords[12]],
                [-40, 0, 0, self.curRecords[13]],
                [-50, 0, 0, self.curRecords[14]],
                [-60, 0, 0, self.curRecords[15]],

                (30, 50, 70),
                (1, 2, 3, 4, 5, 6, 7, 8)
            ],
            [
                [-100, -100, 0.2, self.curRecords[2]],
                [-200, -200, 0.02, self.curRecords[3]],
                [-300, -300, 0.02, self.curRecords[4]],
                [-400, -400, 0.01, self.curRecords[5]],

                [-500, -500, 0.01, self.curRecords[6]],
                [-600, -600, 0.01, self.curRecords[7]],
                [-700, -700, 0.005, self.curRecords[8]],
                [-800, -800, 0.005, self.curRecords[9]],

                [-100, 0, 0, self.curRecords[10]],
                [-200, 0, 0, self.curRecords[11]],
                [-300, 0, 0, self.curRecords[12]],
                [-400, 0, 0, self.curRecords[13]],
                [-500, 0, 0, self.curRecords[14]],
                [-600, 0, 0, self.curRecords[15]],

                (100, 100, 100),
                (1, 4, 8, 16, 32, 64, 128, 256)
            ],
            [
                [-100, -100, 0.2, self.curRecords[2]],
                [-1000, -1000, 0.02, self.curRecords[3]],
                [-10000, -10000, 0.002, self.curRecords[4]],
                [-100000, -100000, 0.0002, self.curRecords[5]],

                [-1000000, -1000000, 0.00002, self.curRecords[6]],
                [-10000000, -10000000, 0.00002, self.curRecords[7]],
                [-100000000, -100000000, 0.00002, self.curRecords[8]],
                [-1000000000, -1000000000, 0.00002, self.curRecords[9]],

                [-1000, 0, 0, self.curRecords[10]],
                [-10000, 0, 0, self.curRecords[11]],
                [-100000, 0, 0, self.curRecords[12]],
                [-1000000, 0, 0, self.curRecords[13]],
                [-10000000, 0, 0, self.curRecords[14]],
                [-100000000, 0, 0, self.curRecords[15]],

                (100, 200, 300),
                (1, 100, 1000, 10000, 50000, 100000, 1000000, 10000000)
            ]
        )
        
        self.running = True
        self.reloadPending = False
        pygame.display.set_icon(pygame.image.load('CoinRedacted.png'))
        self.__openWindow_mainMenu__()

    def __del__(self):
        self.recordsFile.close()
        pygame.quit()

    def __openWindow_mainMenu__(self):
        self.state = 'mainMenu'
        self.mainMenuSize = (400, 600)
        self.screen = pygame.display.set_mode(self.mainMenuSize)
        pygame.display.set_caption('Licker Clicker > Main Menu')
        self.__updateCurrentTheme__()
        lbl = Label(surface=self.screen ,width=400, height=100, x=0, y=0, font=self.theme.labelFont, text='Licker Clicker', color_Text=self.theme.labelColor, alignMode='Center')
        buttonSize = (380, 85)
        buttonTuple = (
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=self.__openWindow_game__, font=self.theme.buttonTextFont, text='Play', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=self.__openWindow_shop__, font=self.theme.buttonTextFont, text='Shop', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=self.__openWindow_settings__, font=self.theme.buttonTextFont, text='Settings', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: os.startfile('help.txt'), font=self.theme.buttonTextFont, text='? Help ?', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=self.__exit__, font=self.theme.buttonTextFont, text='Exit', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive)
            )
        for button in buttonTuple:
                button.center_self_x(self.mainMenuSize[0])
        CenteredElement().arrange_group_y(self.mainMenuSize[1]-lbl.height, 100, 'margin_elements+bordersDown', buttonTuple)
        while self.running:
            self.screen.fill(self.theme.background)
            self.__scanEvents__()
            self.noCursorOverButtons = True
            lbl.draw()
            for button in buttonTuple:
                if (button.update(mouseButton_Up=self.mouseButon_Up)) and self.noCursorOverButtons:
                    self.noCursorOverButtons = False
            
            self.__updateCursor__()
            
            pygame.display.flip()
            self.clock.tick(60)  # limits FPS to 60
        if self.reloadPending:
            self.reloadPending = False
            self.running = True
            self.__openWindow_mainMenu__()
    
    def __openWindow_game__(self):
        def mainButtonPressed():
            Game.clickprojectile(width = 20, height = 20, path='CoinRedacted.png', surface = self.screen, bottomRect = lowerBar, array = clickprojectileArray, impulse = -5,x = pygame.mouse.get_pos()[0], y = pygame.mouse.get_pos()[1])
            self.curRecords[0] += 1+self.curRecords[2]*self.difficulties[self.curDifficulty][15][0]
        def generatePrice(formula):
            return formula[0] + formula[1]*formula[2]*formula[3]
        def checkifFreakingPictureIsFullyRevealed():
            checked_index = 10#индекс первой кнопки из набора оных над картинкой
            index_of_last_FreakingPictureSubButton = 15#Индекс последней кнопки из набора оных над картинкой
            while checked_index <= index_of_last_FreakingPictureSubButton:
                if self.curRecords[checked_index] == 0:
                    return False#Если хоть один элемент от 10 до 15 равен 0, ничего не происходит
                checked_index += 1
            return True
        def leftRightBottomBarsButton_Pressed(index):#first is 0
            #print(index)
            self.__updateCurrentRecords__(index+2, 1)
            self.__updateCurrentRecords__(0, generatePrice(self.difficulties[self.curDifficulty][index]))
            self.difficulties[self.curDifficulty][index][3] = self.curRecords[index+2]

            #проверка, купили ли мы все из 6 кнопок
            if index >= 8:#То есть, проверка происходит только если мы нажали именно одну кнопку из набора оных над картинкой
                #8 не соответствует 10 в функции, так как в текстовом файле с сохранением первые два значения - это не первая и вторая левые кнопки, а
                #монетки и алмазики
                if checkifFreakingPictureIsFullyRevealed():
                    self.__updateCurrentRecords__(1, 100)#Если все элементы от 10 до 15 не равны нулю, добавляется 100 алмазиков
            else:
                self.difficulties[self.curDifficulty][index][3] = self.curRecords[index+2]# there was 'iter' in place of 'index'
                temp_cost = self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][index]))
                temp_quantity = self.__shortenNumberStr__(self.curRecords[index + 2])
                if index <= 3:
                    buttonTuples[0][index].labels_Inactive[1].text = 'Cost: ' + temp_cost + ' coins'
                    buttonTuples[0][index].labels[1].text = 'Cost: ' + temp_cost + ' coins'
                    buttonTuples[0][index].corneredLabel.text = temp_quantity
                else:
                    buttonTuples[1][index-4].labels_Inactive[1].text = 'Cost: ' + temp_cost + ' coins'
                    buttonTuples[1][index-4].labels[1].text = 'Cost: ' + temp_cost + ' coins'
                    buttonTuples[1][index-4].corneredLabel.text = temp_quantity

        self.__performSubLoopStartRoutine__()#SubLoop start routine
        windowWidth, windowHeight = 600, 700
        self.screen = pygame.display.set_mode((windowWidth, windowHeight))
        pygame.display.set_caption('Licker Clicker > Game')
        self.__getInfoFromRecordsFile__()
        self.__updateAllDifficulties__()
        self.__updateCurrentDifficulty__()
        checkifFreakingPictureIsFullyRevealed()#Если картинка внизу полностью открыта, игра сбрасывается, но алмазики остаются.
        
        buttonSize = (85, 85)
        buttonsRow1_x = 7
        buttonsRow2_x = 508
        buttonTuples = (
            (
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow1_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(0), imagePath='L1.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][0]) + ' Coin(s) per click', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][0])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][0])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[2]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthEast'),
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow1_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(1), imagePath='L2.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][1]) + ' Coin(s) every second', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][1])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][1])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[3]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthEast'),
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow1_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(2), imagePath='L3.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][2]) + ' Coin(s) every second', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][2])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][2])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[4]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthEast'),
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow1_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(3), imagePath='L4.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][3]) + ' Coin(s) every second', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][3])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][3])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[5]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthEast')
            ),
            (
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow2_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(4), imagePath='R1.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][4]) + ' Coin(s) every second', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][4])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][4])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[6]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthWest'),
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow2_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(5), imagePath='R2.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][5]) + ' Coin(s) every second', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][5])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][5])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[7]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthWest'),
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow2_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(6), imagePath='R3.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][6]) + ' Coin(s) every second', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][6])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][6])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[8]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthWest'),
                Game.ImageButton_FloatingAndCorneredTexts(width=buttonSize[0], height=buttonSize[1], x=buttonsRow2_x, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: leftRightBottomBarsButton_Pressed(7), imagePath='R4.png', imageCoverArea=1, font=self.theme.floatingLabel_Font, text=['+ ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][15][7]) + ' Coin(s) every second', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][7])) + ' coins'], color_Text=self.theme.buttonTextColor, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=['Not enough coins!', 'Cost: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][7])) + ' coins'], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive, corneredText=self.__shortenNumberStr__(self.curRecords[9]), color_CorneredText=self.theme.corneredTextColor, color_CorneredText_Background=self.theme.corneredTextColor_Background, font_CorneredText=self.theme.corneredText_Font, corneredTextMode='SouthWest')
            )
                )

        elementMargin = 7
        temp_sideBarWidth = buttonSize[0]+elementMargin*2
        temp_upperBarHeight = buttonSize[1]+elementMargin*2
        temp_sideBarHeight = windowHeight-temp_upperBarHeight*3

        imagewidth, imageheight = temp_upperBarHeight-7, temp_upperBarHeight-7
        image_coin = RotationImage(path="CoinRedacted.png" ,width=imagewidth, height=imageheight, x=7, y=0, surface=self.screen)
        image_diamond = RotationImage(path="DiamondRedacted.png" ,width=imagewidth, height=imageheight, x=windowWidth-temp_upperBarHeight, y=0, surface=self.screen)
        image_coin.center_self_y(temp_upperBarHeight)
        image_diamond.center_self_y(temp_upperBarHeight)

        labelwidth = (windowWidth-imagewidth*2)/2
        coinCountLabel = Label(surface=self.screen ,width=labelwidth, height=temp_upperBarHeight, x=imagewidth + 10, y=0, font=self.theme.gameWindowLabelFont_Coin, text='1000000000', color_Text=self.theme.gameWindowLabelColor_Coin, alignMode='Left')
        diamondCountLabel = Label(surface=self.screen ,width=labelwidth, height=temp_upperBarHeight, x=imagewidth - 10 + labelwidth, y=0, font=self.theme.gameWindowLabelFont_Diamond, text='1000', color_Text=self.theme.gameWindowLabelColor_Diamond, alignMode='Right')

        for tuple in buttonTuples:
                CenteredElement().arrange_group_y(temp_sideBarHeight, temp_upperBarHeight, 'margin_elements+borders', tuple)
                for button in tuple:
                    button.updateValues()

        lowerBar = pygame.Rect(0, windowHeight-temp_upperBarHeight*2, windowWidth, temp_upperBarHeight*2)

        clickprojectileArray = []

        mainButton = TextButton(width=windowWidth-elementMargin*2-temp_sideBarWidth*2, height=windowHeight-elementMargin*2-temp_upperBarHeight*3, x=temp_sideBarWidth+elementMargin, y=temp_upperBarHeight+elementMargin, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=mainButtonPressed, font=self.theme.buttonTextFont, text='Click me!', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive)
        
        freakingPicture = Game.checkerboard(width=lowerBar.width/2, height=lowerBar.height, x=lowerBar.x, y=lowerBar.y, rows=2, columns=3, surface=self.screen, imagePath='lock.png', callback=leftRightBottomBarsButton_Pressed, callbackArgumentOffset=8, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, font=self.theme.floatingLabel_Font, text=[['Open this lock! Cost: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][8][0])], ['Open this lock! Cost: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][9][0])], ['Open this lock! Cost: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][10][0])], ['Open this lock! Cost: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][11][0])], ['Open this lock! Cost: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][12][0])], ['Open this lock! Cost: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][13][0])]], color_Text=self.theme.floatingLabel_Color, color_Text_Background=self.theme.floatingLabel_Background, font_Inactive=self.theme.floatingLabel_Font_Inactive, text_Inactive=[['Not enough coins: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][8][0]) + ' required.'],['Not enough coins: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][9][0]) + ' required.'],['Not enough coins: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][10][0]) + ' required.'],['Not enough coins: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][11][0]) + ' required.'],['Not enough coins: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][12][0]) + ' required.'],['Not enough coins: ' + self.__shortenNumberStr__(self.difficulties[self.curDifficulty][13][0]) + ' required.']], color_Text_Inactive=self.theme.floatingLabel_Color_Inactive, color_Text_Background_Inactive=self.theme.floatingLabel_Background_Inactive)
        freakingPicture.center_self_x(lowerBar.width)
        freakingPicture.updateValues()

        rotationCounter = 0
        rotationCounterIncrement = 2
        buttonsEffectsCounter = 0
        while self.subrunning:
            self.screen.fill(self.theme.background)
            self.__scanEvents__()


            #upper bar
            pygame.draw.rect(self.screen, self.theme.upperBarColor, pygame.Rect(0, 0, windowWidth, temp_upperBarHeight))
            #button rows (sidebars)
             #left button row
            pygame.draw.rect(self.screen, self.theme.sideBarColor, pygame.Rect(0, temp_upperBarHeight, temp_sideBarWidth, temp_sideBarHeight))
             #right button row
            pygame.draw.rect(self.screen, self.theme.sideBarColor, pygame.Rect(windowWidth - temp_sideBarWidth, temp_upperBarHeight, temp_sideBarWidth, temp_sideBarHeight))
            #lower bar
            pygame.draw.rect(self.screen, self.theme.lowerBarColor, lowerBar)

            image_coin.draw(rotationCounter)            
            image_diamond.draw(-rotationCounter)

            if buttonsEffectsCounter >= 60:
                buttonsEffectsCounter = 0
                self.__updateCurrentRecords__(0, self.curRecords[3]*self.difficulties[self.curDifficulty][15][1] + self.curRecords[4]*self.difficulties[self.curDifficulty][15][2] + self.curRecords[5]*self.difficulties[self.curDifficulty][15][3] + self.curRecords[6]*self.difficulties[self.curDifficulty][15][4] + self.curRecords[7]*self.difficulties[self.curDifficulty][15][5] + self.curRecords[8]*self.difficulties[self.curDifficulty][15][6] + self.curRecords[9]*self.difficulties[self.curDifficulty][15][7])
            buttonsEffectsCounter += 1

            coinCountLabel.text = self.__shortenNumberStr__(self.curRecords[0])#str(self.curRecords[0])
            
            diamondCountLabel.text = self.__shortenNumberStr__(self.curRecords[1])#str(self.curRecords[1]) 
            
            coinCountLabel.draw()
            diamondCountLabel.draw()
            
            self.noCursorOverButtons = True

            if mainButton.update(mouseButton_Up=self.mouseButon_Up) and self.noCursorOverButtons:
                self.noCursorOverButtons = False
            iter = 0
            for tuple in buttonTuples:
                for button in tuple:
                    if self.curRecords[0] < generatePrice(self.difficulties[self.curDifficulty][iter])*(-1):
                        button.state_Active = False
                    else:
                        button.state_Active = True
                    #self.difficulties[self.curDifficulty][iter][3] = self.curRecords[iter+2]
                    #button.text_Inactive = 'Not enough coins: ' + self.__shortenNumberStr__(generatePrice(self.difficulties[self.curDifficulty][iter])) + ' required.'
                    if button.update(mouseButton_Up=self.mouseButon_Up) and self.noCursorOverButtons:
                        self.noCursorOverButtons = False
                    iter += 1
            
            for element in clickprojectileArray:
                element.update()

            iter = freakingPicture.callbackArgumentOffset
            for innerButton in freakingPicture.array:
                if self.curRecords[iter+2] > 0:
                    freakingPicture.array[iter - freakingPicture.callbackArgumentOffset].state_FullyDisabled = True
                elif self.curRecords[0] < generatePrice(self.difficulties[self.curDifficulty][iter])*(-1):
                    #records file is 16 entries and button variables go like that: [2;15], but formulas array is 14 entries for all the button variables.
                    #essentially, number 8 for formulas erray represents the formula for element, which data is assigned number 10 in records file.
                    #hence the iter+2 when we plan to access the curRecords array and just 'iter' when adressing formulas array 
                    innerButton.state_Active = False
                else:
                    innerButton.state_Active = True
                iter += 1

            freakingPictureUpdateResults = freakingPicture.update(self.mouseButon_Up)
            iter = 0
            for result in freakingPictureUpdateResults:
                match result:
                    case 1:
                        self.noCursorOverButtons = False
                        for label in freakingPicture.array[iter].labels:
                            label.draw()
                    case 2:
                        for label_Inactive in freakingPicture.array[iter].labels_Inactive:
                            label_Inactive.draw()
                iter += 1

            self.__updateCursor__()

            pygame.display.flip()

            if abs(rotationCounter) >= 40:
                rotationCounterIncrement *= -1
            rotationCounter += rotationCounterIncrement

            self.clock.tick(60)  # limits FPS to 60
        if checkifFreakingPictureIsFullyRevealed():
            self.__resetAllButASpecificElementUntil__(ignoredElementIndex=1, startOfResetIndex=0, endOfResetIndex=15)
        self.__setInfoToRecordsFile__()
        self.__performSubLoopEndRoutine__()#SubLoop end routine

    def __openWindow_shop__(self):
        def createSpecificLambda(func, *args):
            return lambda: func(args[0])
        def shopItemPressed(id):
            pressedShopItem = self.__findArrayElementById__(notOwnedThemes, id)
            self.__updateCurrentRecords__(id+16, 1)
            self.__updateCurrentRecords__(1, -int(pressedShopItem.price))
            notOwnedThemes.remove(pressedShopItem)
            CenteredElement().arrange_group_y(allowed_height=windowHeight-elementMargin*2-temp_upperBarHeight, y_offset=elementMargin+temp_upperBarHeight, mode='margin_elements+borders', group=notOwnedThemes)

        self.__performSubLoopStartRoutine__()
        windowWidth, windowHeight = 450, 600
        self.screen = pygame.display.set_mode((windowWidth, windowHeight))
        pygame.display.set_caption('Licker Clicker > Shop')

        self.__getInfoFromRecordsFile__()
        self.__updateCurrentDifficulty__()
        notOwnedThemes = []
        elementIndex, lastElement = 17, 19
        temp_shopThemes = self.shopThemes.copy()
        while elementIndex <= lastElement:
            if self.curRecords[elementIndex] == 0:
                for theme in temp_shopThemes:
                    if theme.id == elementIndex - 16:
                        temp_Lambda = createSpecificLambda(shopItemPressed, theme.id)
                        notOwnedThemes.append(Game.shopItem(width=400, height=150, x=15, y=15, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=temp_Lambda, color_demonstration_small=theme.buttonColor_Hover, color_demonstration_middle=theme.buttonColor, color_demonstration_big=theme.background, font_name=self.theme.shopItem_nameFont, name=theme.name, color_name=self.theme.shopItem_nameColor, color_name_hover=self.theme.shopItem_nameColor_Hover, color_name_mousebutton_down=self.theme.shopItem_nameColor_MouseButton_Down, font_price=self.theme.shopItem_priceFont, price=theme.price, color_price=self.theme.shopItem_priceColor, color_price_hover=self.theme.shopItem_priceColor_Hover, color_price_mousebutton_down=self.theme.shopItem_priceColor_MouseButton_Down, price_imagePath='DiamondRedacted.png', id=int(theme.id)))
                        temp_shopThemes.remove(theme)
                        break
            elementIndex += 1

        elementMargin = 7
        temp_upperBarHeight = 85 + elementMargin*2

        imagewidth, imageheight = temp_upperBarHeight-7, temp_upperBarHeight-7
        labelwidth = (windowWidth-imagewidth*2)/2
        image_diamond = RotationImage(path="DiamondRedacted.png" ,width=imagewidth, height=imageheight, x=windowWidth-temp_upperBarHeight, y=0, surface=self.screen)
        lbl = Label(surface=self.screen ,width=labelwidth, height=temp_upperBarHeight, x=0, y=0, font=self.theme.labelFont, text=' >Shop', color_Text=self.theme.labelColor, alignMode='Left')
        diamondCountLabel = Label(surface=self.screen ,width=labelwidth, height=temp_upperBarHeight, x=imagewidth - 10 + labelwidth, y=0, font=self.theme.gameWindowLabelFont_Diamond, text='1000', color_Text=self.theme.gameWindowLabelColor_Diamond, alignMode='Right')
        
        for shopItem in notOwnedThemes:
            shopItem.center_self_x(parentWidth=windowWidth)
        CenteredElement().arrange_group_y(allowed_height=windowHeight-elementMargin*2-temp_upperBarHeight, y_offset=elementMargin+temp_upperBarHeight, mode='margin_elements+borders', group=notOwnedThemes)
        rotationCounter = 0
        rotationCounterIncrement = 2
        while self.subrunning:
            self.screen.fill(self.theme.background)
            self.__scanEvents__()
            self.noCursorOverButtons = True

            #upper bar
            pygame.draw.rect(self.screen, self.theme.upperBarColor, pygame.Rect(0, 0, windowWidth, temp_upperBarHeight))
            diamondCountLabel.text = self.__shortenNumberStr__(self.curRecords[1])
            diamondCountLabel.draw()
            lbl.draw()
            image_diamond.draw(-rotationCounter)

            for shopItem in notOwnedThemes:
                if int(shopItem.price) > self.curRecords[1]:
                    shopItem.state_Active = False
                else:
                    shopItem.state_Active = True
                if shopItem.update(mouseButton_Up=self.mouseButon_Up) and self.noCursorOverButtons:
                    self.noCursorOverButtons = False
            
            self.__updateCursor__()

            pygame.display.flip()

            if abs(rotationCounter) >= 40:
                rotationCounterIncrement *= -1
            rotationCounter += rotationCounterIncrement

            self.clock.tick(60)
        self.__setInfoToRecordsFile__()
        self.__performSubLoopEndRoutine__()

    def __openWindow_settings__(self):
        def __openWindow_settings_themes__(parentWidth, parentHeight):
            def createSpecificLambda(func, *args):
                return lambda: func(args[0])
            def themePressed(id):
                self.curRecords[16] = id
                self.sub2running = False
                self.subrunning = False
                self.running = False
                self.mouseButon_Up = False
                self.reloadPending = True
            self.__performSub2LoopStartRoutine__()
            windowWidth, windowHeight = 450, 750
            self.screen = pygame.display.set_mode((windowWidth, windowHeight))
            pygame.display.set_caption('Licker Clicker > Settings > Themes')
            self.__getInfoFromRecordsFile__()
            ownedThemes = []
            ownedThemes.append(Game.shopItem(width=400, height=150, x=15, y=15, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: themePressed(self.theme_default.id), color_demonstration_small=self.theme_default.buttonColor_Hover, color_demonstration_middle=self.theme_default.buttonColor, color_demonstration_big=self.theme_default.background, font_name=self.theme.shopItem_nameFont, name=self.theme_default.name, color_name=self.theme.shopItem_nameColor, color_name_hover=self.theme.shopItem_nameColor_Hover, color_name_mousebutton_down=self.theme.shopItem_nameColor_MouseButton_Down, font_price=self.theme.shopItem_priceFont, price=self.theme_default.price, color_price=self.theme.shopItem_priceColor, color_price_hover=self.theme.shopItem_priceColor_Hover, color_price_mousebutton_down=self.theme.shopItem_priceColor_MouseButton_Down, price_imagePath='DiamondRedacted.png', id=int(self.theme_default.id), show_price=False))
            elementIndex, lastElement = 17, 19
            temp_shopThemes = self.shopThemes.copy()
            while elementIndex <= lastElement:
                if self.curRecords[elementIndex] >= 1:
                    for theme in temp_shopThemes:
                        if theme.id == elementIndex - 16:
                            temp_Lambda = createSpecificLambda(themePressed, theme.id)
                            ownedThemes.append(Game.shopItem(width=400, height=150, x=15, y=15, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=temp_Lambda, color_demonstration_small=theme.buttonColor_Hover, color_demonstration_middle=theme.buttonColor, color_demonstration_big=theme.background, font_name=self.theme.shopItem_nameFont, name=theme.name, color_name=self.theme.shopItem_nameColor, color_name_hover=self.theme.shopItem_nameColor_Hover, color_name_mousebutton_down=self.theme.shopItem_nameColor_MouseButton_Down, font_price=self.theme.shopItem_priceFont, price=theme.price, color_price=self.theme.shopItem_priceColor, color_price_hover=self.theme.shopItem_priceColor_Hover, color_price_mousebutton_down=self.theme.shopItem_priceColor_MouseButton_Down, price_imagePath='DiamondRedacted.png', id=int(theme.id), show_price=False))
                            temp_shopThemes.remove(theme)
                            break
                elementIndex += 1
            
            elementMargin = 7
            temp_upperBarHeight = 85 + elementMargin*2
            labelwidth = (windowWidth-(temp_upperBarHeight-7)*2)/2
            lbl = Label(surface=self.screen ,width=labelwidth, height=temp_upperBarHeight, x=0, y=0, font=self.theme.labelFont, text=' >Themes', color_Text=self.theme.labelColor, alignMode='Left')

            for shopItem in ownedThemes:
                shopItem.center_self_x(parentWidth=windowWidth)
            CenteredElement().arrange_group_y(allowed_height=windowHeight-elementMargin*2-temp_upperBarHeight, y_offset=elementMargin+temp_upperBarHeight, mode='margin_elements+borders', group=ownedThemes)
            while self.sub2running:
                self.screen.fill(self.theme.background)
                self.__scanEvents__()
                self.noCursorOverButtons = True

                #upper bar
                pygame.draw.rect(self.screen, self.theme.upperBarColor, pygame.Rect(0, 0, windowWidth, temp_upperBarHeight))
                lbl.draw()

                for shopItem in ownedThemes:
                    if shopItem.update(mouseButton_Up=self.mouseButon_Up) and self.noCursorOverButtons:
                        self.noCursorOverButtons = False

                self.__updateCursor__()

                pygame.display.flip()
                self.clock.tick(60)
            self.__setInfoToRecordsFile__()
            self.__performSub2LoopEndRoutine__(parentWidth, parentHeight, 'Licker Clicker > Settings')
        def __openWindow_settings_difficulties__(parentWidth, parentHeight):
            def difficultyChosen(id):
                self.curRecords[20] = id
                self.__resetAllButASpecificElementUntil__(ignoredElementIndex=1, startOfResetIndex=0, endOfResetIndex=15)
                self.sub2running = False
                self.mouseButon_Up = False
            self.__performSub2LoopStartRoutine__()
            windowWidth, windowHeight = 400, 500
            self.screen = pygame.display.set_mode((windowWidth, windowHeight))
            pygame.display.set_caption('Licker Clicker > Settings > Difficulty')
            self.__getInfoFromRecordsFile__()

            elementMargin = 7
            temp_upperBarHeight = 85 + elementMargin*2
            labelwidth = (windowWidth-(temp_upperBarHeight-7)*2)/2
            lbl = Label(surface=self.screen ,width=labelwidth, height=temp_upperBarHeight, x=0, y=0, font=self.theme.labelFont, text=' >Difficulty', color_Text=self.theme.labelColor, alignMode='Left')
            buttonSize = (380, 85)
            buttonTuple = (
                    TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: difficultyChosen(0), font=self.theme.buttonTextFont, text='Very easy', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                    TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: difficultyChosen(1), font=self.theme.buttonTextFont, text='Normal', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                    TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: difficultyChosen(2), font=self.theme.buttonTextFont, text='Hard', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive)
                )
            for button in buttonTuple:
                    button.center_self_x(400)
            CenteredElement().arrange_group_y(400, 100, 'margin_elements+borders', buttonTuple)
            while self.sub2running:
                self.screen.fill(self.theme.background)
                self.__scanEvents__()
                self.noCursorOverButtons = True

                #upper bar
                pygame.draw.rect(self.screen, self.theme.upperBarColor, pygame.Rect(0, 0, windowWidth, temp_upperBarHeight))
                lbl.draw()
                for button in buttonTuple:
                    if button.update(mouseButton_Up=self.mouseButon_Up) and self.noCursorOverButtons:
                        self.noCursorOverButtons = False
                
                self.__updateCursor__()

                pygame.display.flip()
                self.clock.tick(60)
            self.__setInfoToRecordsFile__()
            self.__performSub2LoopEndRoutine__(parentWidth, parentHeight, 'Licker Clicker > Settings')
        def resetButtonPressed():
            self.__resetAll__()
            self.sub2running = False
            self.subrunning = False
            self.running = False
            self.mouseButon_Up = False
            self.reloadPending = True

        self.__performSubLoopStartRoutine__()
        windowWidth, windowHeight = 400, 500
        self.screen = pygame.display.set_mode((windowWidth, windowHeight))
        pygame.display.set_caption('Licker Clicker > Settings')
        lbl = Label(surface=self.screen ,width=400, height=100, x=0, y=0, font=self.theme.labelFont, text=' >Settings', color_Text=self.theme.labelColor, alignMode='Left')
        buttonSize = (380, 85)
        buttonTuple = (
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=self.__exit__, font=self.theme.buttonTextFont, text='<-Back', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: __openWindow_settings_themes__(windowWidth, windowHeight), font=self.theme.buttonTextFont, text='Themes', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=lambda: __openWindow_settings_difficulties__(windowWidth, windowHeight), font=self.theme.buttonTextFont, text='Difficulty', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive),
                TextButton(width=buttonSize[0], height=buttonSize[1], x=150, y=100, color=self.theme.buttonColor, color_Hover=self.theme.buttonColor_Hover, color_MouseButton_Down=self.theme.buttonColor_MouseButton_Down, color_Inactive=self.theme.buttonColor_Inactive, surface=self.screen, callback=resetButtonPressed, font=self.theme.buttonTextFont, text='Reset', color_Text=self.theme.buttonTextColor, color_Text_Hover=self.theme.buttonTextColor_Hover, color_Text_MouseButton_Down=self.theme.buttonTextColor_MouseButton_Down, color_Text_Inactive=self.theme.buttonTextColor_Inactive)
            )
        for button in buttonTuple:
                button.center_self_x(400)
        CenteredElement().arrange_group_y(400, 100, 'margin_elements+borders', buttonTuple)

        self.__getInfoFromRecordsFile__()
        temp_upperBarHeight = 100
        while self.subrunning:
            self.screen.fill(self.theme.background)
            self.__scanEvents__()
            self.noCursorOverButtons = True

            #upper bar
            pygame.draw.rect(self.screen, self.theme.upperBarColor, pygame.Rect(0, 0, windowWidth, temp_upperBarHeight))
            lbl.draw()
            for button in buttonTuple:
                if button.update(mouseButton_Up=self.mouseButon_Up) and self.noCursorOverButtons:
                    self.noCursorOverButtons = False

            self.__updateCursor__()

            pygame.display.flip()
            self.clock.tick(60)
        self.__setInfoToRecordsFile__()
        self.__performSubLoopEndRoutine__()

    def __exit__(self):
        if self.state == 'subwindow':
            self.subrunning = False
        elif self.state == 'mainMenu':
            self.running = False
        elif self.state == 'sub2window':
            self.sub2running = False

    def __scanEvents__(self):
        self.mouseButon_Up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__exit__()
                return
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseButon_Up = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__exit__()
                    return

    def __performSubLoopStartRoutine__(self):
        self.subrunning = True
        self.state = 'subwindow'
    def __performSub2LoopStartRoutine__(self):
        self.sub2running = True
        self.state = 'sub2window'

    def __performSubLoopEndRoutine__(self):
        self.__updateCurrentTheme__()
        self.screen = pygame.display.set_mode(self.mainMenuSize)
        self.screen.fill(self.theme.background)# to clean the screen after the loop ends
        self.state = 'mainMenu'# to change the state as the main menu cycle doesn't end, and the state declaration is before the main menu loop 
        #                           (so we have to set it back from 'subwindow' to 'mainmenu' there)
        pygame.display.set_caption('Licker Clicker > Main Menu')
    def __performSub2LoopEndRoutine__(self, parentWidth, parentHeight, parentCaption):
        self.__updateCurrentTheme__()
        self.screen = pygame.display.set_mode((parentWidth, parentHeight))
        self.screen.fill(self.theme.background)
        self.state = 'subwindow'
        pygame.display.set_caption(parentCaption)
    
    def __initializeRecordsFile__(self):
        self.recordsFile = open("records.txt", "w")
        for i in range(21):#20
            self.recordsFile.writelines("0.0\n")
        self.recordsFile.close()
    
    def __checkRecordsFileExistance__(self):
        if not os.path.exists("records.txt") or os.stat("records.txt").st_size == 0:#проверка, существует ли файл (1) и есть ли в нём хоть что-то для выведения (2):
            self.__initializeRecordsFile__()

    def __getInfoFromRecordsFile__(self):
        try:
            self.__checkRecordsFileExistance__()
            self.recordsFile.seek(0)
            self.curRecords.clear()
            for i in range(21):#20
                self.curRecords.append(float(self.recordsFile.readline()))
            print(self.curRecords)
        except:
            self.recordsFile.close()
            self.__initializeRecordsFile__()
            self.recordsFile = open("records.txt", "r+")
            self.__getInfoFromRecordsFile__()
    
    def __setInfoToRecordsFile__(self):
        self.__checkRecordsFileExistance__()
        self.recordsFile.seek(0)
        for i in range(21):#20
            self.recordsFile.write(str(float(self.curRecords[i])) + "\n")

    def __updateCursor__(self):
        if self.noCursorOverButtons:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def __findArrayElementById__(self, array, id):
        for element in array:
            if element.id == id:
                return element
        return False
    def __resetAllButASpecificElementUntil__(self, ignoredElementIndex, startOfResetIndex, endOfResetIndex):
        index = startOfResetIndex
        while index < ignoredElementIndex:
            self.curRecords[index] = 0
            index += 1
        index = ignoredElementIndex + 1
        while index <= endOfResetIndex:
            self.curRecords[index] = 0
            index += 1
    def __resetAll__(self):
        index = 0
        for a in self.curRecords:
            self.curRecords[index] = 0
            index += 1
    def __shortenNumberStr__(self, number):
        def divisionWithoutRemainder(number, divider):
            return (number - number%divider)/divider
        def checkIfNumberContainsValue(number, value):
            return number / value >= 1
        if number < 0:
            number *= -1
        shortenedDecimals = ''
        divider = 1
        checkedValue = 1000
        shortenedDecimalsArray = (' K', ' M', ' B', ' T', ' QA', ' QI', ' SX', ' SE', ' O', ' N', ' DE', ' U')
        for iter in range(12):
            if checkIfNumberContainsValue(number, checkedValue):
                shortenedDecimals = shortenedDecimalsArray[iter]
                divider = checkedValue
            else:
                break
            checkedValue *= 1000
        number = divisionWithoutRemainder(number, divider)
        if type(number) == float:
            number = int(number)
        return str(number) + shortenedDecimals

    def __updateCurrentRecords__(self, index, value):
        self.curRecords[index] += value
        if self.curRecords[index] < 0: self.curRecords[index] = 0
    def __updateCurrentTheme__(self):
        self.__getInfoFromRecordsFile__()
        if int(self.curRecords[16]) == 0:
            self.theme = self.theme_default
        else:
            self.theme = self.__findArrayElementById__(self.shopThemes, int(self.curRecords[16]))
    def __updateCurrentDifficulty__(self):
        self.__getInfoFromRecordsFile__()
        temp_difficultyIndex = int(self.curRecords[20])
        if temp_difficultyIndex < 0 or temp_difficultyIndex > 2:
            temp_difficultyIndex = 0
        self.curDifficulty = temp_difficultyIndex
        shopThemeId = 0
        for a in self.shopThemes:
            self.shopThemes[shopThemeId].price = str(self.difficulties[temp_difficultyIndex][14][shopThemeId])
            shopThemeId += 1
    def __updateAllDifficulties__(self):
        self.__getInfoFromRecordsFile__()
        for difficulty in self.difficulties:
            formulaIndex = 0
            while formulaIndex < 8:
                difficulty[formulaIndex][3] = self.curRecords[formulaIndex+2]
                formulaIndex += 1
def main():
    Game()  

if __name__ == '__main__':
    main()