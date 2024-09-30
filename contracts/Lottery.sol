// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import {ConfirmedOwnerWithProposal} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwnerWithProposal.sol";
import {VRFConsumerBaseV2Plus} from "@chainlink/contracts/src/v0.8/vrf/dev/VRFConsumerBaseV2Plus.sol";
import {VRFV2PlusClient} from "@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";
import {VRFCoordinatorV2Interface} from "@chainlink/contracts/src/v0.8/vrf/interfaces/VRFCoordinatorV2Interface.sol";

interface LuckBank {
    function updateStakersRewards(uint256 earnings) external;
}

contract Lottery is ConfirmedOwnerWithProposal, VRFConsumerBaseV2Plus {
    address payable[] public players;
    uint256 public immutable usdEntryFee;
    AggregatorV3Interface internal immutable ethUsdPriceFeed;

    address payable public LuckBankAddress;
    LuckBank public luckBank;

    uint16 public wanted_difficulty_level = 100;
    mapping(Element => uint8) public elements_difficulty_level;

    enum Element {
        rock_paper_scissors_game,
        color_game,
        number_game,
        dark_light_game
    }

    event GuessSubmitted(address indexed guesser, Guess[] guesses);
    event SolutionGenerated(Guess[] solution);

    struct Ticket {
        uint16 difficulty_level;
        Element[] elements;
        Guess[] solution;
        address[] winners;
    }

    Ticket public ticket;
    Ticket[] public tickets_history; // Array to store the history of tickets

    struct Guess {
        Element element;
        uint8 guessValue;
    }

    mapping(address => Guess[][]) public playersGuesses; // address => [[guess,guess,guess],[guess,guess,guess]]

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        WATING_FOR_VRFCOORDINATOR,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    struct RequestStatus {
        bool fulfilled;
        bool exists;
        uint256[] randomWords;
    }

    event RequestSent(uint256 requestId, uint8 numWords);
    event RequestFulfilled(uint256 requestId, uint256[] randomWords);

    uint256 public s_subscriptionId;
    uint256[] public requestIds;
    uint256 public lastRequestId;
    bytes32 public immutable keyHash;
    uint32 public immutable callbackGasLimit = 100000;
    uint8 public immutable requestConfirmations = 3;
    uint8 public immutable numWords = 1;
    mapping(uint256 => RequestStatus) public s_requests;

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        bytes32 _keyHash,
        address payable _LuckBankAddress
    ) VRFConsumerBaseV2Plus(_vrfCoordinator) {
        usdEntryFee = 50 * (10 ** 18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        keyHash = _keyHash;
        // Initial difficulty values
        ticket.difficulty_level = 1;
        elements_difficulty_level[Element.rock_paper_scissors_game] = 3;
        elements_difficulty_level[Element.color_game] = 5;
        elements_difficulty_level[Element.number_game] = 10;
        elements_difficulty_level[Element.dark_light_game] = 2;

        setLuckBank(_LuckBankAddress);
    }

    function setLuckBank(address payable _LuckBankAddress) public onlyOwner {
        LuckBankAddress = _LuckBankAddress;
        luckBank = LuckBank(_LuckBankAddress);
    }

    // Function to get all guesses of a player
    function getSinglePlayerGuesses(
        address player
    ) public view returns (Guess[][] memory) {
        return playersGuesses[player];
    }

    // Function to update the difficulty level of an element
    function setElementDifficulty(
        Element _element,
        uint8 _difficulty
    ) public onlyOwner {
        elements_difficulty_level[_element] = _difficulty;
    }

    function getPlayersGuesses()
        public
        view
        returns (address[] memory, Guess[][][] memory)
    {
        uint16 uniquePlayerCount = 0;

        // Array to keep track of unique addresses found so far
        address[] memory uniqueAddresses = new address[](players.length);

        // Identify unique players
        for (uint16 i = 0; i < players.length; i++) {
            address player = players[i];
            bool isUnique = true;

            // Check if this player is already seen
            for (uint16 j = 0; j < uniquePlayerCount; j++) {
                if (uniqueAddresses[j] == player) {
                    isUnique = false;
                    break;
                }
            }

            if (isUnique) {
                uniqueAddresses[uniquePlayerCount] = player;
                uniquePlayerCount++;
            }
        }

        // Prepare the result arrays with the correct size
        address[] memory playerAddresses = new address[](uniquePlayerCount);
        Guess[][][] memory allGuesses = new Guess[][][](uniquePlayerCount);

        // Collect the guesses for each unique player
        for (uint16 i = 0; i < uniquePlayerCount; i++) {
            address player = uniqueAddresses[i];
            playerAddresses[i] = player;
            allGuesses[i] = playersGuesses[player];
        }

        return (playerAddresses, allGuesses);
    }

    function enter(Guess[] memory _guesses) public payable {
        require(lottery_state == LOTTERY_STATE.OPEN, "Lottery is not open!");
        require(msg.value >= getEntranceFee(), "Not enough ETH!");

        players.push(payable(msg.sender));

        // Create a new Guess array in storage
        Guess[][] storage playerGuessesArray = playersGuesses[msg.sender];
        Guess[] storage currentGuessArray;

        // Add a new Guess array to storage
        playerGuessesArray.push();
        currentGuessArray = playerGuessesArray[playerGuessesArray.length - 1];

        // Copy guesses from memory to storage one by one
        for (uint32 i = 0; i < _guesses.length; i++) {
            currentGuessArray.push(_guesses[i]);
        }

        // Emit event with full lottery guess details
        emit GuessSubmitted(msg.sender, currentGuessArray);
    }

    function getRecentTicket() public view returns (Ticket memory) {
        require(tickets_history.length > 0, "No tickets available");

        Ticket storage lastTicket = tickets_history[tickets_history.length - 1];

        // Return a memory copy of the last ticket
        return lastTicket;
    }

    function getTicket(
        uint256 n
    )
        public
        view
        returns (
            uint16 difficulty_level,
            Element[] memory elements,
            Guess[] memory solution,
            address[] memory winners
        )
    {
        require(n < tickets_history.length, "Invalid ticket index");

        Ticket storage currentTicket = tickets_history[n]; // Renamed local variable

        return (
            currentTicket.difficulty_level,
            currentTicket.elements,
            currentTicket.solution,
            currentTicket.winners
        );
    }

    function getTicketHistory() public view returns (Ticket[] memory) {
        return tickets_history;
    }

    function getTicketDifficulty() public view returns (uint16) {
        return ticket.difficulty_level;
    }

    function getTicketElements() public view returns (Element[] memory) {
        return ticket.elements;
    }

    function getElementDifficulty(
        Element _element
    ) public view returns (uint8) {
        return elements_difficulty_level[_element];
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10 ** 10;
        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
        return costToEnter;
    }

    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        return uint256(price) * 10 ** 10;
    }

    function get_players() public view returns (address payable[] memory) {
        return players;
    }

    function get_subscriptionId() public view returns (uint256) {
        return s_subscriptionId;
    }

    function set_subscriptionId(uint256 _s_subscriptionId) public onlyOwner {
        s_subscriptionId = _s_subscriptionId;
    }

    function set_wanted_difficulty_level(
        uint16 _wanted_difficulty_level
    ) public onlyOwner {
        wanted_difficulty_level = _wanted_difficulty_level;
    }

    function resetTicket() internal {
        tickets_history.push(ticket);

        ticket.difficulty_level = 1;
        delete ticket.elements;
        delete ticket.solution;
        delete ticket.winners;
    }

    function get_random_3_digits(
        uint256 number,
        uint8 nth_digits
    ) public pure returns (uint16) {
        // Ensure that nth_digits is within a reasonable range to avoid overflow
        require(nth_digits < 19, "nth_digits too large"); // 10^18 is the max safe uint256 power

        uint256 tempNumber = number; // Create a local copy of the number
        uint16 result = 0;
        uint8 digit;

        // Calculate the divisor to start extracting from the nth digit
        uint256 divisor = 10 ** (nth_digits + 2);

        // Ensure divisor is not zero and extract digits
        for (uint8 i = 0; i < 3; i++) {
            if (divisor == 0) {
                break; // Stop if divisor is zero to avoid division by zero
            }
            digit = uint8((tempNumber / divisor) % 10); // Extract the digit at the current position
            result += uint16(digit * (10 ** (2 - i))); // Place the digit in the correct position in result
            divisor /= 10; // Move to the next digit to the right
        }

        return result;
    }

    function set_games(uint256 _games_generator_number) internal {
        uint8 index = 0;
        uint8 numElements = uint8(type(Element).max) + 1;

        ticket.difficulty_level = 1;

        while (ticket.difficulty_level < wanted_difficulty_level) {
            uint16 random_3_digit_number = get_random_3_digits(
                _games_generator_number,
                index++
            );
            Element element = Element(random_3_digit_number % numElements);

            ticket.elements.push(element);
            ticket.difficulty_level *= elements_difficulty_level[element];
        }
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "(---) the lottery state needs to be CLOSED"
        );
        lottery_state = LOTTERY_STATE.OPEN;
        if (lastRequestId != 0) {
            set_games(s_requests[lastRequestId].randomWords[0]);
        } else {
            set_games(
                22457654523000873890618985732870744312626094790626683287552762375778023379207
            ); // rundom number for the first lottery elements
        }
    }

    function endLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "(---) the lottery state needs to be OPEN"
        );
        if (players.length > 0) {
            lottery_state = LOTTERY_STATE.WATING_FOR_VRFCOORDINATOR;
            requestRandomWords(false); //put true if wanna pay in eth
        } else {
            lottery_state = LOTTERY_STATE.CLOSED;
            resetTicket();
        }
    }

    function generateGuesses(
        uint256 number
    ) public view returns (Guess[] memory) {
        Element[] memory ticketElements = ticket.elements;
        uint8 numElements = uint8(ticketElements.length);

        Guess[] memory guesses = new Guess[](numElements);

        for (uint8 i = 0; i < numElements; i++) {
            uint16 random_3_digit_number = get_random_3_digits(number, i + 1);
            guesses[i] = Guess({
                element: ticketElements[i],
                guessValue: uint8(
                    (random_3_digit_number %
                        getElementDifficulty(ticketElements[i])) + 1
                )
            });
        }

        return guesses;
    }

    function calculate_winners() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "(---) the lottery state needs to be CALCULATING_WINNER"
        );
        Guess[] memory winningGuesses = generateGuesses(
            s_requests[lastRequestId].randomWords[0]
        );
        address[] memory tempWinners = new address[](players.length);
        uint8 winnersCount = 0;

        // Check each player's guesses
        for (uint16 i = 0; i < players.length; i++) {
            address player = players[i];
            Guess[][] storage playerGuesses = playersGuesses[player];

            // Loop through each set of guesses
            for (uint32 j = 0; j < playerGuesses.length; j++) {
                Guess[] storage guesses = playerGuesses[j];

                // Check if player's guesses match the winning guesses
                if (checkGuesses(guesses, winningGuesses)) {
                    tempWinners[winnersCount] = player;
                    winnersCount++;
                    break; // Move to the next player if a match is found
                }
            }
        }

        // Update the ticket with the solution and winners
        for (uint8 i = 0; i < winningGuesses.length; i++) {
            ticket.solution.push(winningGuesses[i]);
        }

        // Emit the SolutionGenerated event
        emit SolutionGenerated(winningGuesses);

        // Copy `tempWinners` to storage
        for (uint8 i = 0; i < winnersCount; i++) {
            ticket.winners.push(tempWinners[i]);
        }

        // //send 10% to the LuckBank.sol contract
        payLuckBankEarnings();

        // Calculate prize per winner
        uint256 prizePerWinner = winnersCount > 0
            ? address(this).balance / winnersCount
            : 0;

        // Transfer the prize to all winners
        for (uint8 i = 0; i < winnersCount; i++) {
            payable(tempWinners[i]).transfer(prizePerWinner);
        }

        // Reset the playersGuesses
        for (uint16 i = 0; i < players.length; i++) {
            delete playersGuesses[players[i]];
        }

        resetTicket();
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }

    function payLuckBankEarnings() internal {
        //send 10% to the LuckBank.sol contract
        uint256 earnings = address(this).balance / 10;
        LuckBankAddress.transfer(earnings);
        luckBank.updateStakersRewards(earnings);
    }

    function checkGuesses(
        Guess[] memory guesses,
        Guess[] memory winningGuesses
    ) public pure returns (bool) {
        if (guesses.length != winningGuesses.length) return false;

        for (uint8 i = 0; i < guesses.length; i++) {
            if (
                guesses[i].element != winningGuesses[i].element ||
                guesses[i].guessValue != winningGuesses[i].guessValue
            ) {
                return false;
            }
        }

        return true;
    }

    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] calldata _randomWords
    ) internal override {
        require(
            lottery_state == LOTTERY_STATE.WATING_FOR_VRFCOORDINATOR,
            "(---) the lottery state needs to be WATING_FOR_VRFCOORDINATOR"
        );
        require(s_requests[_requestId].exists, "request not found");
        s_requests[_requestId].fulfilled = true;
        s_requests[_requestId].randomWords = _randomWords;
        emit RequestFulfilled(_requestId, _randomWords);

        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
    }
    //---------------------------------------------------
    function requestRandomWords(
        bool enableNativePayment
    ) private returns (uint256 requestId) {
        requestId = s_vrfCoordinator.requestRandomWords(
            VRFV2PlusClient.RandomWordsRequest({
                keyHash: keyHash,
                subId: s_subscriptionId,
                requestConfirmations: requestConfirmations,
                callbackGasLimit: callbackGasLimit,
                numWords: numWords,
                extraArgs: VRFV2PlusClient._argsToBytes(
                    VRFV2PlusClient.ExtraArgsV1({
                        nativePayment: enableNativePayment
                    })
                )
            })
        );
        s_requests[requestId] = RequestStatus({
            randomWords: new uint256[](0),
            exists: true,
            fulfilled: false
        });
        requestIds.push(requestId);
        lastRequestId = requestId;
        emit RequestSent(requestId, numWords);
        return requestId;
    }

    function getRequestStatus(
        uint256 _requestId
    ) external view returns (bool fulfilled, uint256[] memory randomWords) {
        require(s_requests[_requestId].exists, "request not found");
        RequestStatus memory request = s_requests[_requestId];
        return (request.fulfilled, request.randomWords);
    }
}
