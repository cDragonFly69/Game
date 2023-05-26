
import pygame


class Ground(pygame.sprite.Sprite):
    def __init__(self, image_path, position, **kwargs):
        pygame.sprite.Sprite.__init__(self)

        # 加载地面图片
        self.image_0 = pygame.image.load(image_path)
        self.rect_0 = self.image_0.get_rect()
        self.rect_0.left, self.rect_0.bottom = position
        self.image_1 = pygame.image.load(image_path)
        self.rect_1 = self.image_1.get_rect()
        self.rect_1.left, self.rect_1.bottom = self.rect_0.right, self.rect_0.bottom
        self.speed = -10

    # 根据当前速度更新地面位置
    def update(self):
        self.rect_0.left += self.speed
        self.rect_1.left += self.speed
        if self.rect_0.right < 0:  # 如果第一张图片超出边界则让它与第二张图片拼接在一起
            self.rect_0.left = self.rect_1.right
        if self.rect_1.right < 0:  # 如果第二张图片超出边界则让它与第一张图片拼接在一起
            self.rect_1.left = self.rect_0.right

    # 在屏幕上绘制地面图片
    def draw(self, screen):
        screen.blit(self.image_0, self.rect_0)
        screen.blit(self.image_1, self.rect_1)


class Cloud(pygame.sprite.Sprite):
    def __init__(self, image_path, position, **kwargs):
        pygame.sprite.Sprite.__init__(self)

        # 加载云朵图片
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (132, 45))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position

        self.speed = -1

    # 根据当前速度更新云朵位置
    def update(self):
        self.rect = self.rect.move([self.speed, 0])
        if self.rect.right < 0:  # 如果云朵图片超出边界则移除
            self.kill()

    # 在屏幕上绘制云朵图片
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Scoreboard(pygame.sprite.Sprite):
    def __init__(self, score, font_path, position, is_highest=False):
        pygame.sprite.Sprite.__init__(self)

        # 创建得分板对象，并设置显示位置
        self.text = []
        font = pygame.font.Font(font_path, 24)
        self.score = str(score).zfill(5)  # 将分数转成5位字符串形式
        if is_highest:
            self.text = font.render("历史最高分数 :" + self.score, True, (83, 83, 83))
        else:
            self.text = font.render(self.score, True, (83, 83, 83))
        self.rect = self.text.get_rect()
        self.rect.left, self.rect.top = position

    # 在屏幕上绘制得分板
    def draw(self, screen):
        screen.blit(self.text, self.rect)