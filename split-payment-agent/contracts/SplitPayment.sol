// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SplitPayment {
    struct Split {
        address creator;
        address[] recipients;
        uint256[] percentages; // 比例，如 [30, 30, 40] 表示 3:3:4
        uint256 totalAmount;
        bool executed;
    }

    uint256 public splitCount;
    mapping(uint256 => Split) public splits;

    event SplitCreated(uint256 indexed splitId, address indexed creator, uint256 totalAmount);
    event SplitExecuted(uint256 indexed splitId, address indexed creator, uint256 totalAmount);

    /**
     * @notice 创建一个分账计划
     * @param _recipients 接收地址数组
     * @param _percentages 比例数组（总和应为100）
     */
    function createSplit(
        address[] calldata _recipients,
        uint256[] calldata _percentages
    ) external payable {
        require(_recipients.length == _percentages.length, "Length mismatch");
        require(_recipients.length > 0, "Need at least one recipient");
        require(msg.value > 0, "Must send ETH");

        uint256 total = 0;
        for (uint256 i = 0; i < _percentages.length; i++) {
            require(_percentages[i] > 0, "Percentage must be > 0");
            require(_recipients[i] != address(0), "Invalid recipient");
            total += _percentages[i];
        }
        require(total == 100, "Percentages must sum to 100");

        splits[splitCount] = Split({
            creator: msg.sender,
            recipients: _recipients,
            percentages: _percentages,
            totalAmount: msg.value,
            executed: false
        });

        emit SplitCreated(splitCount, msg.sender, msg.value);
        splitCount++;
    }

    /**
     * @notice 执行分账，按比例发送 ETH 给各接收者
     * @param _splitId 分账计划 ID
     */
    function executeSplit(uint256 _splitId) external {
        Split storage s = splits[_splitId];
        require(s.creator == msg.sender, "Only creator can execute");
        require(!s.executed, "Already executed");

        s.executed = true;

        for (uint256 i = 0; i < s.recipients.length; i++) {
            uint256 amount = (s.totalAmount * s.percentages[i]) / 100;
            if (amount > 0) {
                (bool success, ) = s.recipients[i].call{value: amount}("");
                require(success, "Transfer failed");
            }
        }

        emit SplitExecuted(_splitId, msg.sender, s.totalAmount);
    }

    /**
     * @notice 查询分账计划详情
     * @param _splitId 分账计划 ID
     */
    function getSplit(uint256 _splitId) external view returns (
        address creator,
        address[] memory recipients,
        uint256[] memory percentages,
        uint256 totalAmount,
        bool executed
    ) {
        Split storage s = splits[_splitId];
        return (s.creator, s.recipients, s.percentages, s.totalAmount, s.executed);
    }
}
