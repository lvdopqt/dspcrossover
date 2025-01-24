from features.navigator.controller import Navigator

# Mock TwoWayCrossover class
class MockTwoWayCrossover:
    def __init__(self):
        self.display_called = False
        self.on_click_called = False
        self.on_back_called = False
        self.on_right_called = False
        self.on_left_called = False

    def display(self):
        self.display_called = True
        return "Mock TwoWayCrossover Display Text"

    def on_click(self, data=None):
        self.on_click_called = True

    def on_back(self, data=None):
        self.on_back_called = True

    def on_right(self, data=None):
        self.on_right_called = True

    def on_left(self, data=None):
        self.on_left_called = True

# Mock AnotherPage class (for testing flexibility)
class MockAnotherPage:
    def __init__(self):
        self.display_called = False
        self.on_click_called = False
        self.on_back_called = False
        self.on_right_called = False
        self.on_left_called = False

    def display(self):
        self.display_called = True
        return "Mock AnotherPage Display Text"

    def on_click(self, data=None):
        self.on_click_called = True

    def on_back(self, data=None):
        self.on_back_called = True

    def on_right(self, data=None):
        self.on_right_called = True

    def on_left(self, data=None):
        self.on_left_called = True

# Mock LCD class
class MockLCD:
    def __init__(self):
        self.clear_called = False
        self.putstr_called = False
        self.display_text = ""

    def clear(self):
        self.clear_called = True

    def putstr(self, text):
        self.putstr_called = True
        self.display_text = text

# Test initialization with TwoWayCrossover
def test_navigator_initialization_two_way_crossover():
    # Create mock dependencies
    mock_lcd = MockLCD()
    mock_current_page = MockTwoWayCrossover()

    # Create Navigator instance
    navigator = Navigator(
        dsp={},  # Not used in this test
        params={},  # Not used in this test
        lcd=mock_lcd,
        current_page=mock_current_page
    )

    # Verify initial state
    assert isinstance(navigator.current_page, MockTwoWayCrossover), "Current page should be a TwoWayCrossover instance"
    assert mock_lcd.clear_called, "LCD clear should be called on initialization"
    assert mock_lcd.putstr_called, "LCD putstr should be called on initialization"
    assert mock_lcd.display_text == "Mock TwoWayCrossover Display Text", "LCD should display the correct text"
    

# Test initialization with AnotherPage
def test_navigator_initialization_another_page():
    # Create mock dependencies
    mock_lcd = MockLCD()
    mock_current_page = MockAnotherPage()

    # Create Navigator instance
    navigator = Navigator(
        dsp={},  # Not used in this test
        params={},  # Not used in this test
        lcd=mock_lcd,
        current_page=mock_current_page
    )

    # Verify initial state
    assert isinstance(navigator.current_page, MockAnotherPage), "Current page should be an AnotherPage instance"
    assert mock_lcd.clear_called, "LCD clear should be called on initialization"
    assert mock_lcd.putstr_called, "LCD putstr should be called on initialization"
    assert mock_lcd.display_text == "Mock AnotherPage Display Text", "LCD should display the correct text"
    print("[PASS] test_navigator_initialization_another_page")


# Test right event
def test_navigator_right_event():
    # Create mock dependencies
    mock_lcd = MockLCD()
    mock_current_page = MockTwoWayCrossover()

    # Create Navigator instance
    navigator = Navigator(
        dsp={},  # Not used in this test
        params={},  # Not used in this test
        lcd=mock_lcd,
        current_page=mock_current_page
    )

    # Simulate a right event
    navigator.on_right()
    assert navigator.current_page.on_right_called, "on_right should be called on the current page"

# Test left event
def test_navigator_left_event():
    # Create mock dependencies
    mock_lcd = MockLCD()
    mock_current_page = MockTwoWayCrossover()

    # Create Navigator instance
    navigator = Navigator(
        dsp={},  # Not used in this test
        params={},  # Not used in this test
        lcd=mock_lcd,
        current_page=mock_current_page
    )

    # Simulate a left event
    navigator.on_left()
    assert navigator.current_page.on_left_called, "on_left should be called on the current page"