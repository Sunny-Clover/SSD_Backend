-- 使用 SSD 資料庫
USE SSD;

/* ===== 插入會員好友資料的假資料 ===== */
-- 插入假資料到 User 表
INSERT INTO User (Email, Password, Name, Gender, PhotoUrl, InstantPostureAlertEnable, PostureAlertDelayTime, IdleAlertEnable, IdleAlertDelayTime, AverageScore, TotalTime, Level)
VALUES 
('john.doe@example.com', 'password123', 'John Doe', 'Male', 'https://example.com/photos/john.jpg', TRUE, '00:05:00', TRUE, '00:10:00', 85.5, '10:00:00', 5),
('jane.smith@example.com', 'password456', 'Jane Smith', 'Female', 'https://example.com/photos/jane.jpg', FALSE, '00:03:00', TRUE, '00:07:00', 92.3, '12:30:00', 7),
('alex.brown@example.com', 'password789', 'Alex Brown', 'Other', 'https://example.com/photos/alex.jpg', TRUE, '00:04:00', FALSE, '00:08:00', 78.2, '08:45:00', 3),
('emily.white@example.com', 'password321', 'Emily White', 'Female', 'https://example.com/photos/emily.jpg', FALSE, '00:02:00', TRUE, '00:09:00', 88.7, '11:20:00', 6),
('michael.green@example.com', 'password654', 'Michael Green', 'Male', 'https://example.com/photos/michael.jpg', TRUE, '00:06:00', FALSE, '00:12:00', 81.9, '09:50:00', 4);

-- 插入假資料到 FriendRequest 表
INSERT INTO FriendRequest (SenderID, ReceiverID, Status)
VALUES 
(1, 2, 'Pending'),
(2, 3, 'Accepted'),
(3, 4, 'Declined'),
(4, 5, 'Pending'),
(5, 1, 'Accepted');

-- 插入假資料到 FriendList 表
INSERT INTO FriendList (UserID1, UserID2, Status)
VALUES 
(2, 3, 'Accepted'),
(3, 2, 'Accepted'),
(5, 1, 'Accepted'),
(1, 5, 'Accepted');

-- 插入假資料到 BlockedList 表
INSERT INTO BlockedList (BlockerID, BlockedID)
VALUES 
(1, 3),
(2, 4),
(3, 5),
(4, 1),
(5, 2);


/* ===== 插入偵測紀錄的假資料 ===== */
-- 插入假資料到 Record 表
INSERT INTO Record (UserID, StartTime, EndTime, TotalTime, TotalPredictions)
VALUES 
(1, '2023-07-01 08:00:00', '2023-07-01 09:00:00', '01:00:00', 100),
(2, '2023-07-01 09:00:00', '2023-07-01 10:00:00', '01:00:00', 120),
(3, '2023-07-01 10:00:00', '2023-07-01 11:00:00', '01:00:00', 90),
(4, '2023-07-01 11:00:00', '2023-07-01 12:00:00', '01:00:00', 110),
(5, '2023-07-01 12:00:00', '2023-07-01 13:00:00', '01:00:00', 95);

-- 插入假資料到 Body 表
INSERT INTO Body (RecordID, BackwardCount, ForwardCount, NeutralCount)
VALUES 
(1, 30, 40, 30),
(2, 25, 45, 50),
(3, 35, 25, 30),
(4, 20, 50, 40),
(5, 30, 35, 30);

-- 插入假資料到 Feet 表
INSERT INTO Feet (RecordID, AnkleOnKneeCount, FlatCount)
VALUES 
(1, 40, 60),
(2, 30, 90),
(3, 50, 40),
(4, 45, 65),
(5, 35, 60);

-- 插入假資料到 Head 表
INSERT INTO Head (RecordID, BowedCount, NeutralCount, TiltBackCount)
VALUES 
(1, 20, 60, 20),
(2, 25, 70, 25),
(3, 15, 65, 10),
(4, 30, 50, 30),
(5, 20, 60, 15);

-- 插入假資料到 Shoulder 表
INSERT INTO Shoulder (RecordID, HunchedCount, NeutralCount, ShrugCount)
VALUES 
(1, 25, 50, 25),
(2, 30, 60, 30),
(3, 20, 55, 15),
(4, 35, 45, 30),
(5, 25, 50, 20);

-- 插入假資料到 Neck 表
INSERT INTO Neck (RecordID, ForwardCount, NeutralCount)
VALUES 
(1, 40, 60),
(2, 35, 85),
(3, 45, 45),
(4, 30, 80),
(5, 40, 55);
