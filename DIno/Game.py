import core
import sys
import time
import random
import pygame
import sqlite3

from DIno.modules.sprites.obstacle import Food
from modules import *
def main(highest_score):
    # 初始化pygame
    pygame.init()

    # 创建屏幕对象
    screen = pygame.display.set_mode(core.SCREENSIZE)
    pygame.display.set_caption('Dino Rush')

    # 加载音效文件
    sounds = {}
    for key, value in core.AUDIO_PATHS.items():
        sounds[key] = pygame.mixer.Sound(value)

    # 游戏开始界面
    GameStartInterface(screen, sounds, core)

    # 初始化游戏参数
    score = 0
    highest_score = highest_score
    dino = Dinosaur(core.IMAGE_PATHS['dino'])
    ground = Ground(core.IMAGE_PATHS['ground'], position=(0, core.SCREENSIZE[1] * 0.93))
    cloud_sprites_group = pygame.sprite.Group()
    cactus_sprites_group = pygame.sprite.Group()
    ptera_sprites_group = pygame.sprite.Group()
    food_sprites_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    add_obstacle_timer = 0
    add_food_timer = 0
    score_timer = 0
    invincible_time = 0
    food_count = 0
    paused = False
    paused_board = Scoreboard("已暂停，按P继续",core.FONT_PATHS['simhei'], position=(core.SCREENSIZE[0] * 0.5, core.SCREENSIZE[1] * 0.5),)

    # 添加第一个食物
    food_images = Food(core.IMAGE_PATHS['food'], position=(core.SCREENSIZE[0], core.SCREENSIZE[1] * 0.8),sizes=(50,50))
    foods=pygame.sprite.Group()

    # 设置时钟
    clock = pygame.time.Clock()


    while True:
        # 监听游戏事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    dino.jump(sounds)
                elif event.key == pygame.K_DOWN:
                    dino.duck()
                elif event.key == pygame.K_p:
                    paused = not paused # 暂停/继续
                    if paused:
                        paused_board.draw(screen)
                        pygame.display.update()
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                                break
                            elif event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        else:
                            continue
                        break
                elif event.key == pygame.K_f and food_count >= 3:
                    sounds['powerup'].play()
                    invincible_time = time.time()
                    food_count -= 3
                    dino.invincible = True

            elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                dino.unduck()

        # 填充背景色
        screen.fill(core.BACKGROUND_COLOR)

         # 添加云朵
        if len(cloud_sprites_group) < 5 and random.randrange(0, 300) == 10:
            cloud_sprites_group.add(
                Cloud(core.IMAGE_PATHS['cloud'], position=(core.SCREENSIZE[0], random.randrange(30, 200))))

        # 添加障碍物
        add_obstacle_timer += 1
        if add_obstacle_timer > random.randrange(80, 130):
            add_obstacle_timer = 0
            random_value = random.randrange(0, 10)
            if random_value >= 0 and random_value <= 7:
                cactus_sprites_group.add(Cactus(core.IMAGE_PATHS['cacti']))
            else:
                position_ys = [core.SCREENSIZE[1] * 0.82, core.SCREENSIZE[1] * 0.63, core.SCREENSIZE[1] * 0.30]
                ptera_sprites_group.add(
                    Ptera(core.IMAGE_PATHS['ptera'], position=(core.SCREENSIZE[0], random.choice(position_ys))))

        # 添加食物
        if random.randint(0, 1000) == 0:  # 每1000帧生成一个食物，可以根据需要调整
            food_sprites_group.add(Food(core.IMAGE_PATHS['food'], position=(core.SCREENSIZE[0], core.SCREENSIZE[1] * 0.8),sizes=(50,50)))
            food_count += 1

        # 更新角色和障碍物状态
        dino.update()
        ground.update()
        cloud_sprites_group.update()
        cactus_sprites_group.update()
        ptera_sprites_group.update()
        foods.update()

        # 更新分数
        score_timer += 1
        if score_timer > (core.FPS // 12):
            score_timer = 0
            score += 1
            score = min(score, 99999)
            if score > highest_score:
                highest_score = score
            if score % 100 == 0:
                sounds['point'].play()
            if score % 1000 == 0:
                ground.speed -= 1
                for item in cloud_sprites_group:
                    item.speed -= 1
                for item in cactus_sprites_group:
                    item.speed -= 1
                for item in ptera_sprites_group:
                    item.speed -= 1

        # 处理碰撞事件
        if not dino.invincible:
            for item in cactus_sprites_group:
                if pygame.sprite.collide_mask(dino, item):
                    dino.die(sounds)
            for item in ptera_sprites_group:
                if pygame.sprite.collide_mask(dino, item):
                    dino.die(sounds)
        else:
            for item in cactus_sprites_group:
                if pygame.sprite.collide_rect(dino, item):
                    item.kill()
                    sounds['point'].play()
                    score += 100
            for item in ptera_sprites_group:
                if pygame.sprite.collide_rect(dino, item):
                    item.kill()
                    sounds['point'].play()
                    score += 100

        for item in food_sprites_group:
            if pygame.sprite.collide_mask(dino, item):
                sounds['eat'].play()
                score += 20
                item.kill()

        # 绘制所有图形元素
        cloud_sprites_group.draw(screen)

        if not dino.invincible or int(time.time() - invincible_time) % 2 == 0:
            dino.draw(screen)

        ground.draw(screen)
        cactus_sprites_group.draw(screen)
        ptera_sprites_group.draw(screen)
        foods.draw(screen)

        # 显示分数和最高分数
        food_board = Scoreboard("鸡腿数量："+str(food_count), core.FONT_PATHS['simhei'],
                                 position=(core.SCREENSIZE[1] * 0.88, core.SCREENSIZE[1] * 0.1))
        score_board = Scoreboard("当前分数："+str(score), core.FONT_PATHS['simhei'],
                                 position=(core.SCREENSIZE[1] * 0.88, core.SCREENSIZE[1] * 0.05))
        highest_score_board = Scoreboard(highest_score, core.FONT_PATHS['simhei'],
                                         position=(core.SCREENSIZE[0] * 0.72, core.SCREENSIZE[1] * 0.05),
                                         is_highest=True)
        food_board.draw(screen)
        score_board.draw(screen)
        highest_score_board.draw(screen)

        # 显示提示信息
        if food_count >=3:
            info_board = Scoreboard("按F键进入无敌模式，持续5秒钟", core.FONT_PATHS['simhei'],
                                    position=(core.SCREENSIZE[1] * 0.1, core.SCREENSIZE[1] * 0.1))
            info_board.draw(screen)

        # 更新屏幕显示
        pygame.display.update()
        clock.tick(core.FPS)



        # 处理角色死亡事件
        if dino.is_dead:
            c.execute("INSERT INTO record (unix_timestamp, score) VALUES (?,?);", (time.time(), score))
            conn.commit()
            break

        # 处理无敌模式结束事件
        if dino.invincible and time.time() - invincible_time > 5:
            dino.invincible = False

    # 游戏结束界面
    return GameEndInterface(screen, core), highest_score


if __name__ == '__main__':
    # 连接数据库
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # 创建记录表并查询最高分数
    c.execute("CREATE TABLE IF NOT EXISTS record (unix_timestamp INT PRIMARY KEY, score SMALLINT NOT NULL);")
    c.execute("SELECT MAX(score) FROM record;")
    rows = c.fetchall()
    for row in rows:
        highest_score = row[0]
    if not str(highest_score).isdigit():
        highest_score = 0

    # 开始游戏循环
    while True:
        flag, highest_score = main(highest_score)
        if not flag:
            break

    # 提交数据库更改，
    conn.commit()
    conn.close()
