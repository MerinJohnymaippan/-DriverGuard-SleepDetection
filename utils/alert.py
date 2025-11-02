import pygame

pygame.mixer.init()
alert_state = {"drowsiness": False, "phone": False}

def play_alert_sound(alert_type):
    """Play alert sound only when detection occurs."""
    if alert_type not in alert_state:
        return

    if not alert_state[alert_type]:  # Play only if the alert is not already active
        alert_state[alert_type] = True  # Set alert as active

        if alert_type == "drowsiness":
            pygame.mixer.music.load("static/alert_drowsy.mp3")
        elif alert_type == "phone":
            pygame.mixer.music.load("static/alert_phone.mp3")

        pygame.mixer.music.play(-1)  # Play the sound in a loop

def stop_alert_sound(alert_type):
    """Stop alert sound when detection stops."""
    if alert_type in alert_state and alert_state[alert_type]:  # Only stop if it's active
        pygame.mixer.music.stop()  # Stop sound playback
        alert_state[alert_type] = False  # Reset alert state
