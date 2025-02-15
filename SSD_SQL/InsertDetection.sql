-- USE SSD;

DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS InsertMonthlyData (
    IN p_year INT,
    IN p_month INT,
    IN p_userID INT
)
BEGIN
    DECLARE v_startTime DATETIME;
    DECLARE v_endTime DATETIME;
    DECLARE v_DetectionID INT;

    -- 計算 StartTime 和 EndTime
    SET v_startTime = STR_TO_DATE(CONCAT(p_year, '-', p_month, '-01 08:00:00'), '%Y-%m-%d %H:%i:%s');
    SET v_endTime = DATE_ADD(v_startTime, INTERVAL 1 HOUR);

    -- 插入 Detection 表
    INSERT INTO Detection (UserID, StartTime, EndTime, TotalTime, TotalPredictions)
    VALUES (p_userID, v_startTime, v_endTime, '01:00:00', 100 + p_month * 5);

    -- 獲取剛插入的 DetectionID
    SET v_DetectionID = LAST_INSERT_ID();

    -- 插入 Torso 表
    INSERT INTO Torso (DetectionID, BackwardCount, ForwardCount, NeutralCount)
    VALUES (v_DetectionID, 30, 40, 30+ p_month*5);

    -- 插入 Feet 表
    INSERT INTO Feet (DetectionID, AnkleOnKneeCount, FlatCount)
    VALUES (v_DetectionID, 40, 60 + p_month*5);

    -- 插入 Head 表
    INSERT INTO Head (DetectionID, BowedCount, NeutralCount, TiltBackCount)
    VALUES (v_DetectionID, 20, 60 + p_month*5, 20);

    -- 插入 Shoulder 表
    INSERT INTO Shoulder (DetectionID, HunchedCount, NeutralCount, ShrugCount)
    VALUES (v_DetectionID, 25, 50 + p_month*5, 25);

    -- 插入 Neck 表
    INSERT INTO Neck (DetectionID, ForwardCount, NeutralCount)
    VALUES (v_DetectionID, 40, 60 + p_month*5);
END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS InsertYearlyData (
    IN p_year INT,
    IN p_userID INT
)
BEGIN
    DECLARE v_month INT DEFAULT 1;
    DECLARE v_currentDate DATE;

    -- 獲取系統的當前日期
    SET v_currentDate = CURDATE();

    -- 循環從1月插入到12月
    WHILE v_month <= 12 DO
        -- 判斷是否已經超過當前日期
        IF STR_TO_DATE(CONCAT(p_year, '-', v_month, '-01'), '%Y-%m-%d') <= v_currentDate THEN
            CALL InsertMonthlyData(p_year, v_month, p_userID);
        END IF;
        
        -- 增加月份
        SET v_month = v_month + 1;
    END WHILE;
END $$

DELIMITER ;
-- CALL InsertYearlyData(2023, 1);
