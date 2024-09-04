// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import {ConfirmedOwnerWithProposal} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwnerWithProposal.sol";
import {VRFConsumerBaseV2Plus} from "@chainlink/contracts/src/v0.8/vrf/dev/VRFConsumerBaseV2Plus.sol";
import {VRFV2PlusClient} from "@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";
import {VRFCoordinatorV2Interface} from "@chainlink/contracts/src/v0.8/vrf/interfaces/VRFCoordinatorV2Interface.sol";

contract Lottery is ConfirmedOwnerWithProposal, VRFConsumerBaseV2Plus {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    address payable public recentWinner;

    uint16 wanted_difficulty_level = 100;
    mapping(Element => uint8) public elements_difficulty_level;

    enum Element {
        rock_paper_scissors_game,
        color_game,
        number_game,
        dark_light_game
    }

    event GuessSubmitted(address indexed guesser, Guess[] guesses);

    struct Ticket {
        uint16 difficulty_level;
        Element[] elements;
    }

    Ticket public ticket;
    Ticket[] public tickets_history; // Array to store the history of tickets

    struct Guess {
        Element element;
        uint8 guessValue;
    }

    mapping(address => Guess[][]) private playersGuesses; // address => [[guess,guess,guess],[guess,guess,guess]]

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    struct RequestStatus {
        bool fulfilled; // whether the request has been successfully fulfilled
        bool exists; // whether a requestId exists
        uint256[] randomWords;
    }

    event RequestSent(uint256 requestId, uint8 numWords);
    event RequestFulfilled(uint256 requestId, uint256[] randomWords);

    uint256 public s_subscriptionId;
    uint256[] public requestIds;
    uint256 public lastRequestId;
    bytes32 public keyHash;
    uint32 public callbackGasLimit = 100000;
    uint8 public requestConfirmations = 3;
    uint8 public numWords = 1;
    mapping(uint256 => RequestStatus) public s_requests;

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        bytes32 _keyHash
    ) VRFConsumerBaseV2Plus(_vrfCoordinator) {
        usdEntryFee = 50 * (10 ** 18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        keyHash = _keyHash;
        // Initial difficulty values
        elements_difficulty_level[Element.rock_paper_scissors_game] = 3;
        elements_difficulty_level[Element.color_game] = 5;
        elements_difficulty_level[Element.number_game] = 10;
        elements_difficulty_level[Element.dark_light_game] = 2;
    }

    // Function to update the difficulty level of an element
    function setElementDifficulty(
        Element _element,
        uint8 _difficulty
    ) public onlyOwner {
        elements_difficulty_level[_element] = _difficulty;
    }

    // Function to get all guesses of a player
    function getSinglePlayerGuesses(
        address player
    ) public view returns (Guess[][] memory) {
        return playersGuesses[player];
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

    function resetTicket() internal onlyOwner {
        // Store the current ticket in the history
        tickets_history.push(ticket);

        // Reset the ticket to default values
        ticket.difficulty_level = 1;
        delete ticket.elements;
    }

    function get_rundom_digit(
        uint256 number,
        uint8 n
    ) public pure returns (uint8) {
        // Shift the number right by (n-1) digits to bring the desired digit to the least significant position
        for (uint8 i = 1; i < n; i++) {
            number /= 10;
        }
        return uint8(number % 10); // Cast to uint8
    }

    function set_games(uint256 _games_generator_number) internal {
        uint8 index = 0;
        uint8 numElements = uint8(type(Element).max) + 1; // Number of elements in the enum

        // Initialize the ticket difficulty level to 1
        ticket.difficulty_level = 1;

        while (ticket.difficulty_level < wanted_difficulty_level) {
            uint8 digit = get_rundom_digit(_games_generator_number, index++);
            Element element = Element(digit % numElements); // Generate a random element from the digit

            ticket.elements.push(element);
            ticket.difficulty_level *= elements_difficulty_level[element]; // Multiply difficulty
        }
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "(---) the lottery state needs to be CLOSED"
        );
        lottery_state = LOTTERY_STATE.OPEN;
        if (lastRequestId != 0) {
            set_games(s_requests[lastRequestId].randomWords[0]); //idk how to get the latest number
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
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        if (players.length > 0) {
            requestRandomWords(false); //put true if wanna pay in eth
        } else {
            lottery_state = LOTTERY_STATE.CLOSED;
        }

        // Reset the ticket
        resetTicket();

        // Reset the playersGuesses
        for (uint16 i = 0; i < players.length; i++) {
            delete playersGuesses[players[i]];
        }
    }

    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] calldata _randomWords
    ) internal override {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "(---) the lottery state needs to be CALCULATING_WINNER"
        );
        require(s_requests[_requestId].exists, "request not found");
        s_requests[_requestId].fulfilled = true;
        s_requests[_requestId].randomWords = _randomWords;
        emit RequestFulfilled(_requestId, _randomWords);

        uint256 indexOfWinner = _randomWords[0] % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);

        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }
    //---------------------------------------------------
    function requestRandomWords(
        bool enableNativePayment
    ) public onlyOwner returns (uint256 requestId) {
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
