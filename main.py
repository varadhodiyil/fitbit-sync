from service.main import create_app, run_server, fit_bit


def init_token():
    """
    Initiates token Auth
    """
    fit_bit.init_oauth_session()


def main() -> None:
    """
    Enty point
    """
    init_token()
    run_server()


if __name__ == "__main__":
    main()
