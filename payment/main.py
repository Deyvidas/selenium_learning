from payment.authentication import AuthenticationPage
from payment.config.drivers import firefox_driver as driver
from payment.config.profile import user_profile as profile


def main():
    auth = AuthenticationPage(url=profile.auth_url, driver=driver)
    auth.authenticate(profile)


if __name__ == '__main__':
    main()
