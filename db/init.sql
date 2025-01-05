SET GLOBAL event_scheduler = ON;

DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS archive_tasks()
BEGIN
    START TRANSACTION;

    INSERT INTO archived_tasks (
        task_number, 
        user_id, 
        title, 
        description, 
        deadline, 
        importance, 
        was_completed, 
        section, 
        created_at)
    SELECT 
        task_number, 
        user_id, 
        title, 
        description, 
        deadline, 
        importance, 
        is_completed AS was_completed, 
        section, 
        created_at 
    FROM task
    WHERE is_completed = 1 OR is_deleted = 1;

    DELETE FROM task
    WHERE is_completed = 1 OR is_deleted = 1;

    COMMIT;
END$$
DELIMITER ;


CREATE EVENT IF NOT EXISTS ARCHIVE_TASKS
ON SCHEDULE EVERY 1 DAY
DO CALL archive_tasks();
