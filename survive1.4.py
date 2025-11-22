
#!/usr/bin/env python3
#Sheikh Nightshader
#This script is experimental and subject to change
#you can change the wall shading by replacing character shade=" .:-=+*#%@"
import curses, math, time, random

#editing these values below can cause major issues in laggy
MAP_WIDTH = 50
MAP_HEIGHT = 25
FOV = math.pi/3
DEPTH = 20
SCREEN_WIDTH = 70
SCREEN_HEIGHT = 25

MAX_MONSTERS_BASE = 8
MAX_AMMO = 10
MAX_HEALTH = 5
NUM_BOXES = 3

show_gun = True
current_weapon = 1
GUN_OFFSET = 0

def generate_map():
    MAP = ['#'*MAP_WIDTH]
    for _ in range(MAP_HEIGHT-2):
        MAP.append('#' + '.'*(MAP_WIDTH-2) + '#')
    MAP.append('#'*MAP_WIDTH)
    for _ in range(NUM_BOXES):
        w = random.randint(3,6)
        h = random.randint(2,4)
        bx = random.randint(1, MAP_WIDTH-w-1)
        by = random.randint(1, MAP_HEIGHT-h-1)
        for y in range(by, by+h):
            row = list(MAP[y])
            for x in range(bx, bx+w):
                row[x] = '#'
            MAP[y] = ''.join(row)
    return MAP

def spawn_entities(MAP, max_monsters):
    enemies=[]
    pickups=[]
    monster_count=0
    ammo_count=0
    health_count=0
    for y,row in enumerate(MAP):
        for x,ch in enumerate(row):
            if ch=='.':
                r=random.random()
                if r<0.08 and monster_count<max_monsters:
                    enemies.append({'x':x+0.5,'y':y+0.5,'alive':True,'anim':0})
                    monster_count+=1
                elif r<0.12 and ammo_count<MAX_AMMO:
                    pickups.append({'x':x+0.5,'y':y+0.5,'type':'ammo','taken':False})
                    ammo_count+=1
                elif r<0.14 and health_count<MAX_HEALTH:
                    pickups.append({'x':x+0.5,'y':y+0.5,'type':'health','taken':False})
                    health_count+=1
    return enemies, pickups

def cast_rays(player_x,player_y,player_angle,MAP):
    rays=[]
    for col in range(SCREEN_WIDTH):
        ray_angle = player_angle - FOV/2 + (col/SCREEN_WIDTH)*FOV
        distance_to_wall=0
        hit=False
        eye_x=math.sin(ray_angle)
        eye_y=math.cos(ray_angle)
        while not hit and distance_to_wall < DEPTH:
            distance_to_wall+=0.1
            test_x=int(player_x + eye_x*distance_to_wall)
            test_y=int(player_y + eye_y*distance_to_wall)
            if test_x<0 or test_x>=MAP_WIDTH or test_y<0 or test_y>=MAP_HEIGHT:
                hit=True
                distance_to_wall=DEPTH
            elif MAP[test_y][test_x]=='#':
                hit=True
        rays.append(distance_to_wall)
    return rays

def update_bullets(bullets,enemies):
    to_remove=[]
    kills=0
    for b in bullets:
        b['x'] += math.sin(b['angle'])*0.5
        b['y'] += math.cos(b['angle'])*0.5
        if b['x']<0 or b['x']>=MAP_WIDTH or b['y']<0 or b['y']>=MAP_HEIGHT:
            to_remove.append(b)
            continue
        for e in enemies:
            if e['alive'] and int(e['x'])==int(b['x']) and int(e['y'])==int(b['y']):
                e['alive']=False
                kills+=1
                to_remove.append(b)
    bullets=[b for b in bullets if b not in to_remove]
    return bullets,kills

def move_enemies(enemies,player_x,player_y):
    dmg=0
    for e in enemies:
        if not e['alive']: continue
        dx = player_x - e['x']
        dy = player_y - e['y']
        dist = math.hypot(dx,dy)
        if dist < 0.5:
            dmg += 1
        else:
            e['x'] += 0.03*(dx/max(dist,0.1))
            e['y'] += 0.03*(dy/max(dist,0.1))
            e['anim'] = (e['anim']+1)%2
    return dmg

WEAPON_ART = {
    1: [  # Pistol
        r"         ||         ",
        r"        |==|        ",
        r"        |  |        ",
        r"       /|  |\       ",
        r"      | |  | |      ",
    ],
    2: [  # Shotgun
        r"         ||||        ",
        r"        |=||=|       ",
        r"        | || |       ",
        r"       /| || |\      ",
        r"      | | || | |     ",
    ],
    3: [  # Rifle
        r"         |||         ",
        r"        |===|       ",
        r"        |   |       ",
        r"       /|   |\      ",
        r"      | |   | |     ",
        r"     /  |___|  \    ",
    ],
    4: [  # Plasma / sci-fi
        r"        |||||       ",
        r"        |###|       ",
        r"        |###|       ",
        r"       /|###|\      ",
        r"      | |###| |     ",
    ]
}

def draw_gun(stdscr, recoil):
    if not show_gun: return
    gun_art = WEAPON_ART[current_weapon]
    for i, line in enumerate(gun_art):
        stdscr.addstr(SCREEN_HEIGHT - len(gun_art) - GUN_OFFSET + i - recoil,
                      SCREEN_WIDTH//2 - len(line)//2,
                      line,
                      curses.color_pair(3))

def draw_entities(stdscr,player_x,player_y,player_angle,enemies,pickups,bullets):
    for e in enemies:
        if not e['alive']: continue
        dx = e['x'] - player_x
        dy = e['y'] - player_y
        distance = max(math.hypot(dx,dy),0.1)
        angle_to_player = math.atan2(dx,dy)
        angle_diff = angle_to_player - player_angle
        if angle_diff<-math.pi: angle_diff+=2*math.pi
        if angle_diff>math.pi: angle_diff-=2*math.pi
        if abs(angle_diff) < FOV/2:
            col = int(SCREEN_WIDTH/2 + (angle_diff)/(FOV/2)*(SCREEN_WIDTH/2))
            col = max(0, min(SCREEN_WIDTH-3, col-1))
            height = max(1,int(SCREEN_HEIGHT/distance/1.5))
            start = SCREEN_HEIGHT//2 - height//2

            monster_art = ["{©©}","/|\\","/ \\"]

            for i, line in enumerate(monster_art):
                y = start+i
                if 0<=y<SCREEN_HEIGHT-5:
                    color = curses.color_pair(7)
                    stdscr.addstr(y, col, line, color)

    for p in pickups:
        if p['taken']: continue
        dx = p['x'] - player_x
        dy = p['y'] - player_y
        angle_to_player = math.atan2(dx,dy)
        angle_diff = angle_to_player - player_angle
        if angle_diff<-math.pi: angle_diff+=2*math.pi
        if angle_diff>math.pi: angle_diff-=2*math.pi
        if abs(angle_diff) < FOV/2:
            col = int(SCREEN_WIDTH/2 + (angle_diff)/(FOV/2)*(SCREEN_WIDTH/2))
            col = max(0, min(SCREEN_WIDTH-2, col))
            row = SCREEN_HEIGHT//2

            symbol = '♡' if p['type']=='health' else '⌐╦╦═─'
            color = curses.color_pair(6) if p['type']=='health' else curses.color_pair(4)
            stdscr.addstr(row, col, symbol, color)

    for b in bullets:
        dx = b['x'] - player_x
        dy = b['y'] - player_y
        angle_to_player = math.atan2(dx,dy)
        angle_diff = angle_to_player - player_angle
        if angle_diff<-math.pi: angle_diff+=2*math.pi
        if angle_diff>math.pi: angle_diff-=2*math.pi
        if abs(angle_diff)<FOV/2:
            col = int(SCREEN_WIDTH/2 + (angle_diff)/(FOV/2)*(SCREEN_WIDTH/2))
            col = max(0, min(SCREEN_WIDTH-1, col))
            row = SCREEN_HEIGHT//2
            stdscr.addstr(row, col, "*", curses.color_pair(5))

def draw_minimap(stdscr, MAP, player_x, player_y, enemies, pickups):
    map_scale_x = MAP_WIDTH // 20 + 1
    map_scale_y = MAP_HEIGHT // 10 + 1
    for y in range(0, MAP_HEIGHT, map_scale_y):
        for x in range(0, MAP_WIDTH, map_scale_x):
            ch = MAP[y][x]
            draw = ch if ch == '#' else ' '
            stdscr.addch(y//map_scale_y, x//map_scale_x, draw, curses.color_pair(7))
    for p in pickups:
        if not p['taken']:
            px = int(p['x'])//map_scale_x
            py = int(p['y'])//map_scale_y
            symbol = 'H' if p['type']=='health' else 'A'
            stdscr.addch(py, px, symbol, curses.color_pair(4 if p['type']=='ammo' else 6))
    for e in enemies:
        if e['alive']:
            ex = int(e['x'])//map_scale_x
            ey = int(e['y'])//map_scale_y
            stdscr.addch(ey, ex, 'E', curses.color_pair(2))
    stdscr.addch(int(player_y)//map_scale_y, int(player_x)//map_scale_x, 'P', curses.color_pair(3))

def title_screen(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.nodelay(False)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    title = "SURVIVE!! SHEIKHS PyFPS GAME"
    subtitle = "Press ENTER to start"
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height//2-1, width//2 - len(title)//2, title, curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(height//2+1, width//2 - len(subtitle)//2, subtitle, curses.color_pair(2))
    while True:
        key = stdscr.getch()
        if key in (curses.KEY_ENTER, 10, 13):
            break

def game_loop(stdscr):
    global show_gun, current_weapon
    while True:
        wave = 1
        player_x,player_y = MAP_WIDTH/2, MAP_HEIGHT/2
        player_angle = 0.0
        player_health = 25
        ammo = 25
        total_score = 0

        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)

        while player_health>0:
            bullets=[]
            kills=0
            recoil=0
            MAP = generate_map()
            enemies,pickups = spawn_entities(MAP, MAX_MONSTERS_BASE + wave*2)
            start_time = time.time()

            while True:
                stdscr.clear()
                elapsed = int(time.time()-start_time)
                rays = cast_rays(player_x,player_y,player_angle,MAP)

                for y in range(SCREEN_HEIGHT-5):
                    for x in range(SCREEN_WIDTH):
                        distance = rays[x]
                        ceiling = SCREEN_HEIGHT/2 - SCREEN_HEIGHT/distance
                        floor = SCREEN_HEIGHT - ceiling
                        if y < ceiling:
                            stdscr.addch(y, x, ' ', curses.color_pair(6))
                        elif y <= floor:
                            shade = [' ', '.', ',', '-', '~', ':', '%', '$', '&', '#', '@', '▓']
                            idx = int((distance / DEPTH) * (len(shade)-1))
                            ch = shade[len(shade)-1 - idx]
                            stdscr.addch(y,x,ch,curses.color_pair(1))
                        else:
                            stdscr.addch(y,x,'.',curses.color_pair(5))

                draw_gun(stdscr,recoil)
                draw_entities(stdscr,player_x,player_y,player_angle,enemies,pickups,bullets)
                draw_minimap(stdscr, MAP, player_x, player_y, enemies, pickups)

                alive_monsters = sum(1 for e in enemies if e['alive'])
                score = total_score + kills*10 + elapsed
                stdscr.addstr(0,0,f"Wave: {wave} | Health: {player_health} | Ammo: {ammo} | Monsters: {alive_monsters} | Time: {elapsed}s | Score: {score} | Shoot: SPACE | Quit: Q | Toggle Gun: G | Weapons 1-4")

                bullets,new_kills = update_bullets(bullets,enemies)
                kills += new_kills
                dmg = move_enemies(enemies,player_x,player_y)
                if dmg>0: player_health -= dmg

                for p in pickups:
                    if not p['taken'] and int(player_x)==int(p['x']) and int(player_y)==int(p['y']):
                        if p['type']=='ammo': ammo+=5
                        else: player_health = min(player_health+5,25)
                        p['taken']=True

                try: key = stdscr.getch()
                except: key=-1
                recoil=0

                if key in (ord('q'),ord('Q')):
                    return
                elif key==curses.KEY_LEFT: player_angle-=0.1
                elif key==curses.KEY_RIGHT: player_angle+=0.1
                elif key==curses.KEY_UP:
                    nx = player_x + math.sin(player_angle)*0.3
                    ny = player_y + math.cos(player_angle)*0.3
                    if MAP[int(ny)][int(nx)]!='#': player_x,player_y=nx,ny
                elif key==curses.KEY_DOWN:
                    nx = player_x - math.sin(player_angle)*0.3
                    ny = player_y - math.cos(player_angle)*0.3
                    if MAP[int(ny)][int(nx)]!='#': player_x,player_y=nx,ny
                elif key==ord(' '):
                    if ammo>0:
                        bullets.append({'x':player_x,'y':player_y,'angle':player_angle})
                        ammo-=1
                        recoil=1
                elif key in [ord('g'), ord('G')]:
                    show_gun = not show_gun
                elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
                    current_weapon = int(chr(key))

                stdscr.refresh()
                time.sleep(0.02)

                if player_health <= 0:
                    stdscr.clear()
                    final_score = total_score + kills * 10 + elapsed
                    msg1 = "YOU DIED!"
                    msg2 = f"Final Score: {final_score}"
                    msg3 = "Press R to restart or Q to quit"
                    stdscr.addstr(SCREEN_HEIGHT//2 - 1, SCREEN_WIDTH//2 - len(msg1)//2, msg1, curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addstr(SCREEN_HEIGHT//2, SCREEN_WIDTH//2 - len(msg2)//2, msg2, curses.color_pair(3))
                    stdscr.addstr(SCREEN_HEIGHT//2 + 2, SCREEN_WIDTH//2 - len(msg3)//2, msg3, curses.color_pair(1))
                    stdscr.refresh()
                    stdscr.nodelay(False)
                    while True:
                        key = stdscr.getch()
                        if key in (ord('r'), ord('R')):
                            break
                        elif key in (ord('q'), ord('Q')):
                            return
                    stdscr.nodelay(True)
                    break

                if alive_monsters==0:
                    total_score=score
                    wave+=1
                    stdscr.addstr(SCREEN_HEIGHT//2, SCREEN_WIDTH//2-6,f"WAVE {wave-1} CLEARED")
                    stdscr.addstr(SCREEN_HEIGHT//2+1, SCREEN_WIDTH//2-10,f"Score: {score}")
                    stdscr.addstr(SCREEN_HEIGHT//2+2, SCREEN_WIDTH//2-15,"Press any key for next wave")
                    stdscr.refresh()
                    stdscr.nodelay(False)
                    stdscr.getch()
                    stdscr.nodelay(True)
                    break

if __name__=="__main__":
    curses.wrapper(title_screen)
    curses.wrapper(game_loop)
