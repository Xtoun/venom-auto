import time
from selenium.webdriver.common.by import By

from wallet import venom
from app.account import AccountLoader
from app.base import VenomAuto
from app.config import get_logger, ACC_VENOM_PATH

logger = get_logger(__name__)


CONFIG = {
    "environment": "test",
    "mainnet": {
    },
    "test": {
        "twitter": {
            "venom_network": "https://twitter.com/Venom_network_",
            "venom_foundation": "https://twitter.com/VenomFoundation",
        },
        "task": {
            "venom_foundation": "https://venom.network/tasks/venom-foundation",
            "venom_wallet": "https://venom.network/tasks/venom-wallet",
            "web3_world": "https://venom.network/tasks/web3-world",
            "venom_stake": "https://venom.network/tasks/venom-stake",
            "venom_pad": "https://venom.network/tasks/venom-pad",
            "oasis_gallery": "https://venom.network/tasks/oasis-gallery",
        },
        "app": {
            "venom_stake": "https://testnet.venomstake.com/",
        }
    },
}
VENOM_ADDRESS = "0:077873f1453fa67b0f1ce77f1e806675acd19c4694b9738be61fd406618f2f7a"
FOLLOW_XP = "//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]/div/span/span"


class Venom(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def incentive(self, account: dict = None):

        url = f"https://venom.network/tasks"
        self.driver.get(url)
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        # click on the Connect Wallet button
        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(7)
        self.auto.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[2]/span', 2)
        self.auto.click("//div[contains(text(),'Venom Chrome')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.click("//div[contains(text(),'Connect')]", 3)

        # login twitter and discord
        self.auto.switch_to_window(0)
        self.login_twitter(account)
        self.driver.close()
        # self.auto.switch_to_window(0)
        # self.login_discord(account)
        # self.driver.close()

        # main incentive
        # self.auto.switch_to_window(0)
        # self._daily_faucet(account)
        self.auto.switch_to_window(0)
        self._venom_pad(account)
        self.auto.switch_to_window(0)
        self._venom_stake(account)
        self.auto.switch_to_window(0)
        self._foundation(account)
        self.auto.switch_to_window(0)
        self._venom_wallet(account)
        self.auto.switch_to_window(0)
        self._web3_world(account)
        self.auto.switch_to_window(0)
        self._oasis_gallery(account)
        self.auto.switch_to_window(0)
        self._bridge(account)

        logger.info(f"Incentive success")

    def balance(self, account):
        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])
        self.auto.switch_to_window(0)
        self.driver.get(venom.POPUP_URL)
        time.sleep(2)
        balance = self.auto.try_find('//*[@id="root"]/div/div[1]/div[2]/div[1]/div/div[1]/div/div/div[2]')
        if balance:
            balance = balance.text.split(".")[0]
            logger.info(f"Balance: {balance}")
            account['balance'] = balance

        logger.info(f"process account success")

    def send_wallet(self, account):
        amount = self.params.get('amount', 1)
        receiver = VENOM_ADDRESS
        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])
        self.auto.switch_to_window(0)
        self.driver.get(venom.POPUP_URL)
        time.sleep(3)

        balance = self.auto.try_find('//*[@id="root"]/div/div[1]/div[2]/div[1]/div/div[1]/div/div/div[2]')
        if balance:
            balance = balance.text.split(".")[0]
            logger.info(f"Balance: {balance}")
            account['balance'] = balance

        self._get_address(account)

        self.auto.switch_to_window(0)
        self.auto.send(receiver=receiver, amount=amount)

        self.auto.switch_to_window(0)
        time.sleep(1)
        logger.info(f"send ${amount} VENOM to {receiver} success")

    def _get_address(self, account):
        self.auto.try_click('//*[@id="root"]/div/div[1]/div[2]/div[1]/div/div[1]/div/div/div[1]/div[1]/div', 2)
        self.auto.try_click('//*[@id="root"]/div/div[1]/div[2]/div[1]/div/div[1]/div/div/div[1]/div[1]/div/div/ul/li[2]/button', 7)
        self.auto.switch_to_window(-1)
        address = self.auto.try_find('//*[@id="root"]/div/main/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div')
        if address:
            address = address.text
            logger.info(f"Address: {address}")
            account['address'] = address
        self.driver.close()

    def _venom_stake(self, acc: dict = None):
        try:
            self.driver.get(self.config['task']['venom_stake'])
            time.sleep(5)

            self.auto.try_click("//button[contains(text(),'Check')]", 4)

            self.auto.click("//button[contains(text(),'Mint')]", 4)
            self.auto.confirm(acc['password'])
        except Exception as e:
            logger.error(e)

    def _venom_pad(self, acc: dict = None):
        try:
            self.driver.get(self.config['task']['venom_pad'])
            time.sleep(5)
            follow_tw = self.auto.try_find("//a[contains(text(),'Follow')]")
            if not follow_tw:
                # job done, move on
                return

            follow_tw.click()
            time.sleep(6)

            # they will popup a new window for twitter follow, go to that window
            self.auto.switch_to_window(-1)
            tweet_tw = self.auto.try_find(FOLLOW_XP)
            if tweet_tw:
                tweet_tw.click()
                self.driver.close()
                time.sleep(5)  # must wait for venom to check twitter follow
            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 20)

            # wait to solve captcha
            while len(self.driver.window_handles) == 1:
                self.auto.try_click("//button[contains(text(),'Check')]")
                time.sleep(20)

            if len(self.driver.window_handles) > 1:
                # they may popup a new window for twitter follow again, go to that window and follow it
                # and then close window
                self.auto.switch_to_window(-1)
                self.auto.try_click(FOLLOW_XP, 4)
                self.driver.close()

            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)

            self.auto.try_click("//a[contains(text(),'Tweet')]", 4)
            # they will popup new tab for tweet
            self.auto.switch_to_window(-1)
            tweet_tw = self.auto.try_find("//span[contains(text(),'Tweet')]")
            if tweet_tw:
                tweet_tw.click()
                self.driver.close()
                time.sleep(30)
            self.auto.switch_to_window(0)
            self.auto.try_click("//button[contains(text(),'Check')]", 30)

            self.auto.click("//button[contains(text(),'Mint')]", 4)
            self.auto.confirm(acc['password'])
        except Exception as e:
            logger.error(e)

    def _first_task(self, acc: dict = None):
        login_tw = self.auto.try_find("//button[contains(text(),'Login with Twitter')]")
        if login_tw:
            login_tw.click()
            time.sleep(4)
            self.auto.try_click("allow", time_to_sleep=10, by=By.ID)
            self.auto.switch_to_window(1)

        follow_btn = self.auto.try_find("//a[contains(text(),'Follow')]")
        if follow_btn:
            follow_btn.click()
            time.sleep(4)
            self.auto.switch_to_window(-1)
            self.auto.try_click('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]/div/span/span', 10)
            self.driver.close()
            self.auto.switch_to_window(0)
            time.sleep(55)
            self.auto.try_click("//button[contains(text(),'Check')]", 5)

        claim_btn = self.auto.try_find("//button[contains(text(),'Claim')]")
        if claim_btn:
            claim_btn.click()
            time.sleep(4)
            self.auto.sign()
            time.sleep(5)

    def _foundation(self, acc: dict = None):
        try:
            self.auto.switch_to_window(-1)
            self.driver.get(self.config['task']['venom_foundation'])
            time.sleep(8)

            follow_tw = self.auto.try_find("//a[contains(text(),'Follow')]")
            if not follow_tw:
                return

            follow_tw.click()
            time.sleep(6)

            self.auto.switch_to_window(-1)
            fl_again_tw = self.auto.try_find(FOLLOW_XP)
            if fl_again_tw:
                fl_again_tw.click()
                self.driver.close()
                time.sleep(20)
            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)

            if len(self.driver.window_handles) > 1:
                # they may popup a new window for twitter follow again, go to that window and follow it
                # and then close window
                self.auto.switch_to_window(-1)
                self.auto.try_click(
                    "//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]/div/span/span", 4
                )
                self.driver.close()

            fl_again_tw = self.auto.try_find(FOLLOW_XP)
            if fl_again_tw:
                fl_again_tw.click()
                self.driver.close()
                time.sleep(20)
            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)

            self.auto.try_click("//a[contains(text(),'Tweet')]", 4)
            self.auto.switch_to_window(-1)
            tweet_tw = self.auto.try_find("//span[contains(text(),'Tweet')]")
            if tweet_tw:
                tweet_tw.click()
                self.driver.close()
                time.sleep(20)
            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 30)

            self.auto.try_click("//button[contains(text(),'Mint')]", 4)
            self.auto.confirm(acc['password'])
        except Exception as e:
            logger.error(e)

    def _venom_wallet(self, acc: dict = None):
        try:
            self.driver.get(self.config['task']['venom_wallet'])
            time.sleep(8)

            check_button = self.auto.try_find("//button[contains(text(),'Check')]")
            if check_button:
                self.auto.send(receiver=VENOM_ADDRESS, amount='1')

            time.sleep(4)
            self.auto.switch_to_window(0)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)
            self.auto.click("//button[contains(text(),'Mint')]", 6)
            self.auto.confirm(acc['password'])
        except Exception as e:
            logger.error(e)

    def daily_faucet(self, account: dict = None):
        url = f"https://venom.network/faucet"
        self.driver.get(url)
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        # click on the Connect Wallet button
        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(4)
        self.auto.try_click('//*[@id="root"]/div[1]/div[1]/div[2]/div[2]/span', 2)
        self.auto.try_click("//div[contains(text(),'Venom Chrome')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.try_click("//div[contains(text(),'Connect')]", 3)
        self._daily_faucet()
        logger.info(f"Faucet claim successfull for {account['address']}")

    def _daily_faucet(self, account: dict = None):
        try:
            url = f"https://venom.network/faucet"
            self.auto.switch_to_window(-1)
            self.driver.get(url)
            time.sleep(5)
            answer = self.params.get('answer')
            self.auto.try_click("//a[contains(text(), 'Start')]", 3)
            self.auto.try_click(f"//span[contains(text(), '{answer}')]", 3)
            self.auto.try_click("//button[contains(text(), 'Send')]", 7)
            self.auto.try_click("//span[contains(text(), 'Claim')]", 3)
            self.auto.sign()
            time.sleep(15)
            logger.info(f"Faucet claim successfull for {account['address']}")
        except Exception as e:
            logger.error(e)

    def _web3_world(self, acc: dict = None):
        try:
            self.driver.get(self.config['task']['web3_world'])
            time.sleep(5)

            follow_tw = self.auto.try_find("//a[contains(text(),'Follow')]")
            if follow_tw:
                follow_tw.click()
                time.sleep(3)
            else:
                self.auto.open_new_tab("https://twitter.com/intent/user?screen_name=w3w_exchange")
                self.auto.switch_to_window(-1)
                time.sleep(5)

            self.auto.switch_to_window(-1)
            fl_tw = self.auto.try_find(FOLLOW_XP)
            if fl_tw:
                fl_tw.click()
                self.driver.close()
                time.sleep(10)
            self.auto.switch_to_window(0)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)

            self.auto.try_click("//button[contains(text(),'Mint')]", 6)
            self.auto.confirm(acc['password'])
        except Exception as e:
            logger.error(e)

    def _oasis_gallery(self, acc: dict = None):
        try:
            self.auto.switch_to_window(-1)
            self.driver.get(self.config['task']['oasis_gallery'])
            time.sleep(4)

            follow_tw = self.auto.try_find("//a[contains(text(),'Follow')]")
            if not follow_tw:
                self.driver.close()
                return

            follow_tw.click()
            time.sleep(6)
            self.auto.switch_to_window(-1)
            fl_again_tw = self.auto.try_find(FOLLOW_XP)
            if fl_again_tw:
                fl_again_tw.click()
                time.sleep(6)
                self.driver.close()
            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)

            fl_again_tw = self.auto.try_find(FOLLOW_XP)
            if fl_again_tw:
                fl_again_tw.click()
                time.sleep(20)
                self.driver.close()
            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)

            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Mint')]", 6)
            self.auto.confirm(acc['password'])
        except Exception as e:
            logger.error(e)

    def _bridge(self, acc: dict = None):
        try:
            self.auto.switch_to_window(-1)
            self.driver.get(self.config['task']['oasis_gallery'])
            time.sleep(4)

            follow_tw = self.auto.try_find("//a[contains(text(),'Follow')]")
            if not follow_tw:
                self.driver.close()
                return

            follow_tw.click()
            time.sleep(6)
            self.auto.switch_to_window(-1)
            fl_again_tw = self.auto.try_find(FOLLOW_XP)
            if fl_again_tw:
                fl_again_tw.click()
                time.sleep(6)
                self.driver.close()
            self.auto.switch_to_window(-1)
            self.auto.try_click("//button[contains(text(),'Check')]", 4)
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    # list_account = AccountLoader().parser_file()
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    swap_params = {
        "account": list_account[1],
    }
    params = {
        "list_add": list_account,
        "answer": "All of the above",
        "amount": "1",
    }
    try:
        vn = Venom(
            use_uc=True,
            params=params
        )
        # vn.process_all(method="send_wallet")
        # vn.send_wallet(**swap_params)
        vn.process_all(method="incentive")
        # vn.balance(**swap_params)
        # vn.daily_faucet(**swap_params)
    except Exception as e:
        logger.error(e)
