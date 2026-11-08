PROGRAM MAIN
VAR
	axis_x : AXIS_REF;
	axis_y : AXIS_REF;
	
	power_x : MC_Power;
	power_y : MC_Power;
	
	move_x : MC_MoveAbsolute;
	move_y : MC_MoveAbsolute;
	
	target_x : LREAL;
	target_y : LREAL;
	
	execute : BOOL := FALSE;
	state : INT := 0;
END_VAR

VAR CONSTANT
	velocity : LREAL := 4.0;
	
	x_max : LREAL := 50.0;
	x_min : LREAL := -50.0;
	
	y_max : LREAL := 100.0;
	y_min : LREAL := -100.0;
END_VAR

//------------------------------------------------------------------------------

axis_x.ReadStatus();
axis_y.ReadStatus();

power_x(
    Axis            := axis_x,
    Enable          := TRUE,
    Enable_Positive := TRUE,
    Enable_Negative := TRUE,
    Override        := 100);

power_y(
    Axis            := axis_y,
    Enable          := TRUE,
    Enable_Positive := TRUE,
    Enable_Negative := TRUE,
    Override        := 100);

move_x(
    Axis     := axis_x,
    Execute  := (state = 1) AND power_x.Status,
    Position := target_x,
    Velocity := velocity);

move_y(
    Axis     := axis_y,
    Execute  := (state = 1) AND power_y.Status,
    Position := target_y,
    Velocity := velocity);

CASE state OF
    0: // WAIT FOR TARGET
        IF execute THEN
			IF target_x <= x_max AND target_x >= x_min AND target_y <= y_max AND target_y >= y_min THEN
            	state := 1;
			ELSE
				state := 3;
			END_IF
        END_IF

    1: // MOVE
        IF move_x.Done AND move_y.Done THEN
            state := 2;
		ELSIF  move_x.Error OR move_y.Error OR move_x.CommandAborted OR move_y.CommandAborted THEN
			state :=3;
        END_IF

    2: // MOVEMENT DONE
        execute := FALSE;
        state   := 0;
		
	3: // ERROR
		execute := FALSE;
END_CASE