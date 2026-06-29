import pygame


WIDTH = 1400
HEIGHT = 900
NODE_RADIUS = 22
MARGIN = 80

pygame.init()

FONT = pygame.font.SysFont("Arial", 18, bold=True)
SMALL = pygame.font.SysFont("Arial", 14)

COLORS = {
    "red": (220, 60, 60),
    "green": (50, 180, 80),
    "blue": (70, 120, 255),
    "yellow": (255, 215, 0),
    "gray": (120, 120, 120),
    "white": (255, 255, 255),
    "black": (25, 25, 25),
}

ZONE_COLORS = {
    "normal": (70, 170, 255),
    "priority": (60, 220, 100),
    "restricted": (255, 160, 40),
    "blocked": (80, 80, 80),
}


class GraphViewer:

    def __init__(self, graph):
        self.graph = graph
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fly-In Graph")

        self.clock = pygame.time.Clock()

        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1

        self.dragging = False

        self.compute_transform()

    def compute_transform(self):
        xs = [z.x for z in self.graph.zones.values()]
        ys = [z.y for z in self.graph.zones.values()]

        minx = min(xs)
        maxx = max(xs)

        miny = min(ys)
        maxy = max(ys)

        graph_w = maxx - minx + 1
        graph_h = maxy - miny + 1

        sx = (WIDTH - 2 * MARGIN) / graph_w
        sy = (HEIGHT - 2 * MARGIN) / graph_h

        self.scale = min(sx, sy)

        self.origin_x = minx
        self.origin_y = miny

    def world_to_screen(self, x, y):

        px = (x - self.origin_x) * self.scale + MARGIN + self.offset_x
        py = (y - self.origin_y) * self.scale + MARGIN + self.offset_y

        py = HEIGHT - py

        return int(px), int(py)

    def draw_grid(self):

        step = 80

        for x in range(0, WIDTH, step):
            pygame.draw.line(
                self.screen,
                (235, 235, 235),
                (x, 0),
                (x, HEIGHT),
            )

        for y in range(0, HEIGHT, step):
            pygame.draw.line(
                self.screen,
                (235, 235, 235),
                (0, y),
                (WIDTH, y),
            )

    def draw_connections(self):

        drawn = set()

        for zone in self.graph.zones.values():

            for c in zone.connections:

                pair = tuple(sorted((c.first.name, c.second.name)))

                if pair in drawn:
                    continue

                drawn.add(pair)

                x1, y1 = self.world_to_screen(c.first.x, c.first.y)
                x2, y2 = self.world_to_screen(c.second.x, c.second.y)

                pygame.draw.line(
                    self.screen,
                    (60, 60, 60),
                    (x1, y1),
                    (x2, y2),
                    3,
                )

                mx = (x1 + x2) // 2
                my = (y1 + y2) // 2

                text = SMALL.render(
                    str(c.dron_capacity),
                    True,
                    (200, 30, 30),
                )

                self.screen.blit(text, (mx, my))

    def draw_zones(self):

        for zone in self.graph.zones.values():

            x, y = self.world_to_screen(zone.x, zone.y)

            color = ZONE_COLORS.get(
                zone.zone_type,
                (120, 170, 255)
            )

            if zone.color:
                color = COLORS.get(zone.color, color)

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                NODE_RADIUS,
            )

            pygame.draw.circle(
                self.screen,
                (0, 0, 0),
                (x, y),
                NODE_RADIUS,
                2,
            )

            if zone == self.graph.start:
                pygame.draw.circle(
                    self.screen,
                    (0, 255, 0),
                    (x, y),
                    NODE_RADIUS + 6,
                    3,
                )

            if zone == self.graph.end:
                pygame.draw.circle(
                    self.screen,
                    (255, 215, 0),
                    (x, y),
                    NODE_RADIUS + 6,
                    3,
                )

            txt = FONT.render(zone.name, True, (0, 0, 0))

            rect = txt.get_rect(center=(x, y - 35))
            self.screen.blit(txt, rect)

            cap = SMALL.render(
                f"{len(zone.drones)}/{zone.max_dron}",
                True,
                (0, 0, 0),
            )

            r = cap.get_rect(center=(x, y + 35))
            self.screen.blit(cap, r)

            if zone.drones:

                n = len(zone.drones)

                angle = 0

                for drone in zone.drones:

                    dx = x + 12 * pygame.math.Vector2(1, 0).rotate(angle).x
                    dy = y + 12 * pygame.math.Vector2(1, 0).rotate(angle).y

                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        (int(dx), int(dy)),
                        6,
                    )

                    angle += 360 / n

    def run(self):

        while True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:
                        self.dragging = True

                    if event.button == 4:
                        self.scale *= 1.1

                    if event.button == 5:
                        self.scale /= 1.1

                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False

                if event.type == pygame.MOUSEMOTION and self.dragging:

                    self.offset_x += event.rel[0]
                    self.offset_y += event.rel[1]

            self.screen.fill((250, 250, 250))

            self.draw_grid()
            self.draw_connections()
            self.draw_zones()

            pygame.display.flip()
            self.clock.tick(60)
