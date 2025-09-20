class BackgroundParticle:
    def __init__(self):
        # Random position in the background
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(120, 380)
        self.base_x = CENTER[0] + radius * math.cos(angle)
        self.base_y = CENTER[1] + radius * math.sin(angle)
        self.x = self.base_x + random.uniform(-10, 10)
        self.y = self.base_y + random.uniform(-10, 10)
        self.float_phase = random.uniform(0, 2 * math.pi)
        self.float_speed = random.uniform(0.0002, 0.0007)
        self.size = random.randint(3, 6)  # Larger
        self.color = (64, 120, 200)  # Brighter blue
        self.alpha = random.randint(120, 200)  # More visible

    def update(self, t):
        # Gentle floating motion
        self.x += math.sin(t * self.float_speed + self.float_phase) * 0.2
        self.y += math.cos(t * self.float_speed + self.float_phase) * 0.2
        # Slowly return to base position
        self.x += (self.base_x - self.x) * 0.002
        self.y += (self.base_y - self.y) * 0.002

    def draw(self, screen):
        surf = pygame.Surface((self.size*4, self.size*4), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color + (self.alpha,), (self.size*2, self.size*2), self.size)
        screen.blit(surf, (int(self.x)-self.size*2, int(self.y)-self.size*2))
import pygame
import sys
import math
import random
from datetime import datetime
import pandas as pd
from sun_times import fetch_sun_times, get_sun_position_fraction
from data_fetcher import DataFetcher

# Visualization settings

WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
PARTICLE_COUNT = 4000  # More, denser particles
RADIUS = 60  # Smaller sun core
BREATH_SPEED = 0.45  # Slower breathing
REPEAT_COUNT = 4  # Number of repeated sun figures
REPEAT_ROTATION_STEP = 2 * math.pi / 7  # Rotation offset for each repeat
REPEAT_OFFSET = 18  # Pixel offset for each repeat

# Subtle color gradient for unity effect
import colorsys
def get_gradient_palette(n):
    base_hue = 0.55  # blue/cyan region in HSV (0.5~0.6)
    # Use a wider hue range and more levels for richer gradients, but in a cooler spectrum
    return [tuple(int(c*255) for c in colorsys.hsv_to_rgb(base_hue + 0.13*(i/n), 0.7, 1.0)) for i in range(n)]
COLOR_PALETTE = get_gradient_palette(96)


class Particle:
    def __init__(self, angle, color, is_spike=False, spike_idx=0):
        self.angle = angle + random.uniform(-0.05, 0.05)
        self.spread_factor = random.random() ** 1.7  # Bias toward center
        self.base_angle = self.angle
        self.base_spread = self.spread_factor
        self.base_radius = RADIUS + self.spread_factor * 240  # Increased from 180 to 240 for more spread
        self.radius = self.base_radius + random.uniform(-12, 12) * (1 + self.spread_factor)  # Increased random range
        # Store base color for later color multiplication
        self.base_color = color
        # Vary speed more for layering
        self.speed = random.uniform(0.0002, 0.0045) * (0.7 + 0.6 * self.spread_factor)
        self.color = color
        self.phase = random.uniform(0, 2 * math.pi)
        self.is_spike = is_spike
        self.spike_idx = spike_idx
        self.bloom_seed = random.uniform(0, 1000)

    def update(self, t, shape_mode=0, blend=0.0, next_shape=0, color1=(255,255,255), color2=(255,255,255)):
        breath = math.sin(t * BREATH_SPEED + self.phase) * 32
        # Unique bloom pattern for each shape and transition
        now_sec = int(t)
        # Use a different random seed for each second to get a new bloom
        bloom_seed = (now_sec + shape_mode * 100 + next_shape * 1000) % 10000 + self.bloom_seed
        # Sun: flower with 8-12 petals
        petal_count_sun = 8 + int(4 * math.fabs(math.sin(bloom_seed)))
        petal_phase_sun = bloom_seed * 0.13
        base_r_sun = RADIUS + self.base_spread * 120 + 30 * math.sin(self.base_angle * petal_count_sun + petal_phase_sun)
        # Moon: flower with 5-7 petals, crescent offset
        petal_count_moon = 5 + int(2 * math.fabs(math.cos(bloom_seed)))
        petal_phase_moon = bloom_seed * 0.21
        base_r_moon = RADIUS + 80 + 180 * math.sin(self.base_angle) + 200 * math.sin(self.base_angle * 2)
        base_r_moon += 24 * math.sin(self.base_angle * petal_count_moon + petal_phase_moon)
        if math.cos(self.base_angle) > 0:
            base_r_moon -= 180 * math.cos(self.base_angle)
        # Cloud: flower with 12-18 petals, amorphous
        petal_count_cloud = 12 + int(6 * math.fabs(math.sin(bloom_seed * 0.7)))
        petal_phase_cloud = bloom_seed * 0.33
        base_r_cloud = RADIUS + 100 + 120 * math.sin(self.base_angle * 2 + t) + 90 * math.sin(self.base_angle * 3 + t * 0.7) + 60 * math.sin(self.base_angle * 5 + t * 1.3) + 40 * math.sin(self.base_angle * 7 + t * 0.5)
        base_r_cloud += 18 * math.sin(self.base_angle * petal_count_cloud + petal_phase_cloud)
        # Flower: more petals, more organic
        petal_count_flower = 16 + int(8 * math.fabs(math.sin(bloom_seed * 0.3)))
        petal_phase_flower = bloom_seed * 0.41
        base_r_flower = RADIUS + 80 + 60 * math.sin(self.base_angle * petal_count_flower + petal_phase_flower) + 40 * math.sin(self.base_angle * 2 + t * 0.8)

        # Interpolate between current and next shape for smooth transition
        # shape_mode: 0=sun, 1=moon, 2=cloud, 3=flower
        if shape_mode == 0 and next_shape == 1:
            base_r = (1-blend) * base_r_sun + blend * base_r_moon
        elif shape_mode == 1 and next_shape == 2:
            base_r = (1-blend) * base_r_moon + blend * base_r_cloud
        elif shape_mode == 2 and next_shape == 3:
            base_r = (1-blend) * base_r_cloud + blend * base_r_flower
        elif shape_mode == 3 and next_shape == 0:
            base_r = (1-blend) * base_r_flower + blend * base_r_sun
        else:
            if shape_mode == 0:
                base_r = base_r_sun
            elif shape_mode == 1:
                base_r = base_r_moon
            elif shape_mode == 2:
                base_r = base_r_cloud
            elif shape_mode == 3:
                base_r = base_r_flower
            else:
                base_r = base_r_sun
        self.radius = base_r + breath * 0.25 + random.uniform(-10, 10)
        self.angle += self.speed * random.uniform(0.7, 1.3)
        # Smoothly interpolate color, then multiply for richness
        interp_color = tuple(
            int((1-blend)*color1[i] + blend*color2[i]) for i in range(3)
        )
        # Multiply color by a factor based on spread_factor for richness
        factor = 0.7 + 0.7 * self.spread_factor + 0.2 * math.sin(self.base_angle + t)
        self.color = tuple(
            min(255, max(0, int(interp_color[i] * factor))) for i in range(3)
        )

    def get_pos(self):
        x = CENTER[0] + self.radius * math.cos(self.angle)
        y = CENTER[1] + self.radius * math.sin(self.angle)
        return int(x), int(y)


class SunTotem:
    def __init__(self, particle_count, color_palette):
        self.particles = []
        for i in range(particle_count):
            angle = 2 * math.pi * i / particle_count
            color = color_palette[i % len(color_palette)]
            p = Particle(angle, color)
            # Allow more spread: keep particles with spread_factor < 0.97
            if p.spread_factor < 0.97:
                self.particles.append(p)
        self.converge = False
        self.converge_progress = 0.0

    def update(self, t, converge=False, shape_mode=0, blend=0.0, next_shape=0, color1=(255,255,255), color2=(255,255,255)):
        self.converge = converge
        for i, p in enumerate(self.particles):
            p.update(t, shape_mode=shape_mode, blend=blend, next_shape=next_shape, color1=color1[i % len(color1)], color2=color2[i % len(color2)])
            if self.converge:
                p.radius += (RADIUS - p.radius) * 0.1
        if self.converge:
            self.converge_progress += 0.02
        else:
            self.converge_progress = 0.0

    def draw(self, screen, global_rotation=0.0):
        # Repeat the sun figure several times with rotation and offset
        for r in range(REPEAT_COUNT):
            angle_offset = r * REPEAT_ROTATION_STEP
            offset_x = int(REPEAT_OFFSET * math.cos(angle_offset))
            offset_y = int(REPEAT_OFFSET * math.sin(angle_offset))
            # Global scaling for expansion/reduction
            global_scale = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() / 700.0)
            # Additional movement: elliptical and spiral
            spiral_phase = pygame.time.get_ticks() / 1200.0
            for p in self.particles:
                # Apply global rotation, rotation and offset to each particle
                rotated_angle = p.angle + angle_offset + global_rotation
                dist = p.radius * global_scale
                # Elliptical motion
                ellipse_x = math.cos(rotated_angle) * dist * (1.0 + 0.18 * math.sin(spiral_phase + p.base_angle))
                ellipse_y = math.sin(rotated_angle) * dist * (0.85 + 0.22 * math.cos(spiral_phase + p.base_angle * 1.5))
                # Spiral motion
                spiral = 18 * math.sin(spiral_phase + p.base_angle * 2)
                x = CENTER[0] + int(ellipse_x + spiral) + offset_x
                y = CENTER[1] + int(ellipse_y + spiral) + offset_y
                size = 1  # All particles are now even smaller
                if random.random() < (1.0 - 0.45 * p.spread_factor):
                    pygame.draw.circle(screen, p.color, (x, y), size)
                if random.random() < 0.18 * (1.0 - p.spread_factor):
                    pygame.draw.circle(screen, p.color, (x + random.randint(-1,1), y + random.randint(-1,1)), size)
        if self.converge and self.converge_progress > 0.8:
            for r in range(40, 0, -4):
                color = COLOR_PALETTE[0]
                pygame.draw.circle(screen, color, CENTER, r)

def get_current_color_palette():
    hour = datetime.now().hour
    # Rotate palette so current hour is first
    return COLOR_PALETTE[hour:] + COLOR_PALETTE[:hour]

def should_converge(events):
    now = datetime.now()
    # Placeholder: check if now matches sunrise, sunset, month start, or moonset
    return False

def main():
    # Create a pool of background particles
    BG_PARTICLE_COUNT = 400  # More background particles
    bg_particles = [BackgroundParticle() for _ in range(BG_PARTICLE_COUNT)]
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mystical Sun Totem Visualization")
    # Try to bring the window to the front (Windows only)
    try:
        import ctypes
        hwnd = pygame.display.get_wm_info()["window"]
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        print("[Info] Could not bring window to front:", e)
    print("[Info] Pygame window created. If you still can't see it, check your display settings.")
    clock = pygame.time.Clock()

    # Fetch sunrise and sunset times
    try:
        sunrise, sunset = fetch_sun_times()
    except Exception as e:
        print("[Error] Could not fetch sun times:", e)
        sunrise, sunset = "06:11", "18:25"  # fallback

    sun_totem = SunTotem(PARTICLE_COUNT, get_current_color_palette())
    t = 0
    last_color_change = -1
    palette = get_current_color_palette()
    font = pygame.font.SysFont('consolas', 12)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # Dynamic background: base color from sun position
        # Update and draw background particles
        for bgp in bg_particles:
            bgp.update(t)
            bgp.draw(screen)
        base_bg = (10, 10, 30)
        # Use sun_frac if available, else fallback
        try:
            bg_frac = sun_frac
        except:
            bg_frac = 0.0
        # Interpolate background color from night to day to sunset
        def bg_color(frac):
            # Even darker, cooler tones: deep navy and blue-black
            if frac <= 0.0:
                return (4, 8, 18)
            elif frac >= 1.0:
                return (12, 18, 28)
            elif frac < 0.5:
                f = frac/0.5
                return (
                    int((1-f)*4 + f*20),
                    int((1-f)*8 + f*24),
                    int((1-f)*18 + f*48)
                )
            else:
                f = (frac-0.5)/0.5
                return (
                    int((1-f)*20 + f*12),
                    int((1-f)*24 + f*18),
                    int((1-f)*48 + f*28)
                )
        bg = bg_color(bg_frac)
        screen.fill(bg)

        # Overlay subtle, slow-moving color ripples
        ripple_count = 6
        t_ripple = pygame.time.get_ticks() / 2000.0
        for i in range(ripple_count):
            # Ripple parameters
            phase = t_ripple + i * 0.7
            radius = int(180 + 180 * math.sin(phase + i))
            alpha = int(32 + 32 * math.sin(phase * 0.7 + i))
            # Ripple color: close to bg, slightly lighter or darker
            ripple_col = tuple(
                min(255, max(0, c + int(18 * math.sin(phase + j*0.8))))
                for j, c in enumerate(bg)
            )
            # Draw ripple as a translucent circle
            ripple_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surf, ripple_col + (alpha,), CENTER, radius)
            screen.blit(ripple_surf, (0, 0))
        # Change color palette every second, but shape morphs smoothly
        now_sec = int(pygame.time.get_ticks() / 1000)
        morph_period = 1.0  # seconds per morph
        morph_t = (pygame.time.get_ticks() / 1000) % morph_period
        blend = morph_t / morph_period
        shape_mode = now_sec % 4
        next_shape = (shape_mode + 1) % 4
        # Get sun position as a fraction between sunrise and sunset
        # Update color every second based on sun's position
        # Animate color: pulse every second, influenced by sun position
        sun_frac = get_sun_position_fraction(sunrise, sunset)
        sec_pulse = 0.5 * (1 + math.sin(2 * math.pi * (pygame.time.get_ticks() % 1000) / 1000.0))  # 0..1 pulse every second
        def sun_color(frac, pulse):
            # Night: (30,60,120), Day: (255,255,180), Sunset: (255,120,40)
            if frac <= 0.0:
                base = (30,60,120)
            elif frac >= 1.0:
                base = (255,120,40)
            elif frac < 0.5:
                f = frac/0.5
                base = tuple(int((1-f)*30 + f*255) if i<2 else int((1-f)*120 + f*180) for i in range(3))
            else:
                f = (frac-0.5)/0.5
                base = (
                    int((1-f)*255 + f*255),
                    int((1-f)*255 + f*120),
                    int((1-f)*180 + f*40)
                )
            # Pulse: brighten or shift hue slightly
            r, g, b = base
            r = min(255, int(r + 30 * pulse))
            g = min(255, int(g + 30 * pulse))
            b = min(255, int(b + 30 * pulse))
            return (r, g, b)
        particle_color = sun_color(sun_frac, sec_pulse)
        palette = [particle_color for _ in range(PARTICLE_COUNT)]
        sun_totem.update(t, converge=False, shape_mode=shape_mode, blend=blend, next_shape=next_shape, color1=palette, color2=palette)

        # Add slow global rotation (e.g., 0.08 radians per second)
        global_rotation = t * 0.08
        sun_totem.draw(screen, global_rotation=global_rotation)

        # Display real-time sun movement data as digital text
        info_color = (255, 255, 255)  # White
        info_lines = [
            f"Time: {datetime.now().strftime('%H:%M:%S')}",
            f"Sunrise: {sunrise}",
            f"Sunset: {sunset}",
            f"Sun position: {sun_frac:.2f}",
            f"Center: {CENTER}",
            f"Radius: {RADIUS}",
            f"Repeat: {REPEAT_COUNT}",
            f"Particles: {PARTICLE_COUNT}",
            f"Frame: {int(t * 50)}"
        ]
        for idx, line in enumerate(info_lines):
            text = font.render(line, True, info_color)
            screen.blit(text, (WIDTH - 180, 180 + idx * 15))

        pygame.display.flip()
        t += 0.02
        clock.tick(60)

if __name__ == "__main__":
    main()
