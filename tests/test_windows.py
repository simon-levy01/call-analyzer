from conversation_copilot import windows


def snapshot(
    title: str,
    path: str,
    *,
    visible: bool = True,
    minimized: bool = False,
    cloaked: bool = False,
):
    return windows._WindowSnapshot(1, title, path, visible, minimized, cloaked)


def test_only_supported_visible_call_windows_are_eligible():
    assert (
        windows._eligible(snapshot("Video call", r"C:\Apps\WhatsApp.exe")).kind
        == "WhatsApp"
    )
    assert (
        windows._eligible(snapshot("Video call", r"C:\Apps\WhatsApp.Root.exe")).kind
        == "WhatsApp"
    )
    assert windows._eligible(snapshot("Meeting", r"C:\Apps\Zoom.exe")).kind == "Zoom"
    meet = windows._eligible(
        snapshot("Team sync - Google Meet", r"C:\Program Files\Google\Chrome\chrome.exe")
    )
    assert meet and meet.kind == "Google Meet"
    active_meet = windows._eligible(
        snapshot("Meet - abc-defg-hij - Google Chrome", r"C:\Program Files\Google\Chrome\chrome.exe")
    )
    assert active_meet and active_meet.kind == "Google Meet"


def test_generic_chrome_and_other_browsers_are_rejected():
    assert windows._eligible(snapshot("WhatsApp", r"C:\Apps\WhatsApp.Root.exe")) is None
    assert windows._eligible(snapshot("Inbox", r"C:\Chrome\chrome.exe")) is None
    assert windows._eligible(snapshot("Meet - search results - Google Chrome", r"C:\Chrome\chrome.exe")) is None
    assert windows._eligible(snapshot("Meet - ABC-DEFG-HIJ - Google Chrome", r"C:\Chrome\chrome.exe")) is None
    assert windows._eligible(snapshot("Google Meet", r"C:\Edge\msedge.exe")) is None
    assert windows._eligible(snapshot("Google Meet", r"C:\Firefox\firefox.exe")) is None


def test_hidden_minimized_and_cloaked_windows_are_rejected():
    path = r"C:\Apps\Zoom.exe"
    assert windows._eligible(snapshot("Call", path, visible=False)) is None
    assert windows._eligible(snapshot("Call", path, minimized=True)) is None
    assert windows._eligible(snapshot("Call", path, cloaked=True)) is None


def test_revalidation_keeps_exact_hwnd_kind_and_process_path(monkeypatch):
    selected = windows.CallWindow(10, "Google Meet", r"C:\Chrome\chrome.exe", "Google Meet", 42)
    monkeypatch.setattr(windows, "eligible_window", lambda hwnd: selected if hwnd == 10 else None)
    assert windows.still_eligible(selected)

    changed_path = windows.CallWindow(10, "Google Meet", r"D:\Fake\chrome.exe", "Google Meet", 42)
    monkeypatch.setattr(windows, "eligible_window", lambda _hwnd: changed_path)
    assert not windows.still_eligible(selected)

    changed_process = windows.CallWindow(
        10, "Google Meet", r"C:\Chrome\chrome.exe", "Google Meet", 43
    )
    monkeypatch.setattr(windows, "eligible_window", lambda _hwnd: changed_process)
    assert not windows.still_eligible(selected)


def test_whatsapp_call_hides_chrome_meet_but_not_zoom():
    whatsapp = windows.CallWindow(1, "Video call", "WhatsApp.exe", "WhatsApp", 10)
    meet = windows.CallWindow(2, "Google Meet", "chrome.exe", "Google Meet", 20)
    zoom = windows.CallWindow(3, "Meeting", "Zoom.exe", "Zoom", 30)

    assert windows._apply_call_priority([meet, zoom]) == [meet, zoom]
    assert windows._apply_call_priority([meet, whatsapp, zoom]) == [whatsapp, zoom]


def test_whatsapp_priority_check_ignores_idle_or_other_call_apps(monkeypatch):
    meet = windows.CallWindow(2, "Google Meet", "chrome.exe", "Google Meet", 20)
    whatsapp = windows.CallWindow(1, "Video call", "WhatsApp.exe", "WhatsApp", 10)

    monkeypatch.setattr(windows, "_enumerate_call_windows", lambda: [meet])
    assert not windows.whatsapp_call_active()
    monkeypatch.setattr(windows, "_enumerate_call_windows", lambda: [meet, whatsapp])
    assert windows.whatsapp_call_active()


def test_capture_availability_rejects_minimized_state(monkeypatch):
    monkeypatch.setattr(
        windows,
        "_snapshot_window",
        lambda _hwnd: snapshot("Call", r"C:\Apps\Zoom.exe", minimized=True),
    )

    assert not windows.window_available(1)
