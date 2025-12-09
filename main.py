import pygame
from pygame import mixer

from src.game import Game
from src.shop import Shop
from src.ui import MainMenu, SettingsMenu
from src.save_manager import SaveManager
from src.asset_loader import AssetLoader
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, MUSIC_PATH


def main():
    pygame.init()
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.mixer.init()

    VIRTUAL_WIDTH = SCREEN_WIDTH
    VIRTUAL_HEIGHT = SCREEN_HEIGHT
    virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    WINDOW_WIDTH = 480
    WINDOW_HEIGHT = 853
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tower Bloxx")

    asset_loader = AssetLoader()
    icon = asset_loader.load_icon()
    pygame.display.set_icon(icon)

    backgrounds = asset_loader.load_backgrounds()

    sounds = asset_loader.load_sounds()
    click_sound = sounds["click"]
    error_sound = sounds["error"]

    current_track_index = 0
    pygame.mixer.music.load(f"{MUSIC_PATH}song_{current_track_index + 1}.mp3")
    pygame.mixer.music.play(-1)

    save_manager = SaveManager()
    clock = pygame.time.Clock()

    music_muted = False
    sfx_muted = False

    state = "menu"
    previous_state = None

    game = None
    shop = None

    main_menu = MainMenu(virtual_screen, click_sound=click_sound)
    settings_menu = SettingsMenu(virtual_screen, click_sound=click_sound)

    current_bg_index = 0

    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type in (
                pygame.MOUSEMOTION,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
            ):
                real_x, real_y = event.pos
                virtual_x = int(real_x * VIRTUAL_WIDTH / WINDOW_WIDTH)
                virtual_y = int(real_y * VIRTUAL_HEIGHT / WINDOW_HEIGHT)
                event.pos = (virtual_x, virtual_y)
                if hasattr(event, "dict"):
                    event.dict["pos"] = (virtual_x, virtual_y)

            if state == "menu":
                action = main_menu.handle_event(event)
                if action == "play":
                    state = "game"
                    game = Game(
                        virtual_screen,
                        save_manager,
                        asset_loader,
                        sound_muted=sfx_muted,
                    )
                elif action == "shop":
                    previous_state = "menu"
                    state = "shop"
                    shop = Shop(
                        virtual_screen,
                        save_manager,
                        asset_loader,
                        click_sound=click_sound,
                        error_sound=error_sound,
                    )
                elif action == "settings":
                    state = "settings"
                    settings_menu.music_muted = music_muted
                    settings_menu.sfx_muted = sfx_muted
                    settings_menu.bg_index = current_bg_index
                    settings_menu.music_index = current_track_index
                elif action == "quit":
                    running = False

            elif state == "settings":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"
                else:
                    action = settings_menu.handle_event(event)
                    if action == "back":
                        state = "menu"
                    elif action == "mute_music":
                        music_muted = not music_muted
                        settings_menu.music_muted = music_muted
                        pygame.mixer.music.set_volume(0.0 if music_muted else 1.0)
                    elif action == "mute_sfx":
                        sfx_muted = not sfx_muted
                        settings_menu.sfx_muted = sfx_muted
                        for s in sounds.values():
                            s.set_volume(0.0 if sfx_muted else 1.0)
                        if game:
                            game.sound_muted = sfx_muted
                            for s in game.sounds.values():
                                s.set_volume(0.0 if sfx_muted else 1.0)
                    elif action == "toggle_bg":
                        current_bg_index = settings_menu.bg_index
                    elif action == "music_change":
                        current_track_index = settings_menu.music_index
                        pygame.mixer.music.load(
                            f"{MUSIC_PATH}song_{current_track_index + 1}.mp3"
                        )
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.0 if music_muted else 1.0)

            elif state == "game":
                if game:
                    if not game.game_over:
                        action = game.handle_game_events(event)
                        if action == "confirm_exit":
                            state = "menu"
                            game = None
                        elif action == "restart_game":
                            game = Game(
                                virtual_screen,
                                save_manager,
                                asset_loader,
                                sound_muted=sfx_muted,
                            )
                    else:
                        result = game.handle_game_over_input(event)
                        if result == "menu":
                            state = "menu"
                            game = None
                        elif result == "shop":
                            previous_state = "game_over"
                            state = "shop"
                            shop = Shop(
                                virtual_screen,
                                save_manager,
                                asset_loader,
                                click_sound=click_sound,
                                error_sound=error_sound,
                            )
                        elif result == "restart":
                            game = Game(
                                virtual_screen,
                                save_manager,
                                asset_loader,
                                sound_muted=sfx_muted,
                            )

            elif state == "shop":
                if shop:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if previous_state == "game_over":
                            state = "game"
                        else:
                            state = "menu"
                    else:
                        action = shop.handle_event(event)
                        if action == "back":
                            if previous_state == "game_over":
                                state = "game"
                            else:
                                state = "menu"

        virtual_screen.fill(WHITE)

        if state == "menu":
            main_menu.draw(backgrounds[current_bg_index])
        elif state == "settings":
            settings_menu.draw(backgrounds[current_bg_index])
        elif state == "game":
            if game:
                if not game.game_over:
                    game.update()
                    game.draw()
                else:
                    game.draw_game_over_screen()
        elif state == "shop":
            if shop:
                shop.draw(backgrounds[current_bg_index])

        scaled = pygame.transform.smoothscale(
            virtual_screen, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        screen.blit(scaled, (0, 0))
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
