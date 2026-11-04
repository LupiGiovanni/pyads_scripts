PROGRAM MAIN
VAR
	axis_x : AXIS_REF;
	axis_y : AXIS_REF;

	power_x : MC_Power;
	power_y : MC_Power;

	move_x : MC_MoveAbsolute;
	move_y : MC_MoveAbsolute;

	reset_x : MC_Reset;
	reset_y : MC_Reset;

	target_x : LREAL;
	target_y : LREAL;

	execute   : BOOL := FALSE;
	state     : INT  := 0;
	
	dx, dy, dist : LREAL;
	kx, ky       : LREAL;

	vel_x, vel_y : LREAL;
	acc_x, acc_y : LREAL;
	dec_x, dec_y : LREAL;
	jrk_x, jrk_y : LREAL;
END_VAR

VAR CONSTANT
	velocity     : LREAL := 4.0;
	acceleration : LREAL := 20.0;
	deceleration : LREAL := 20.0;
	jerk         : LREAL := 100.0;

	min_param : LREAL := 0.001;
	min_dist  : LREAL := 0.001;

	x_max : LREAL := 50.0;
	x_min : LREAL := -50.0;

	y_max : LREAL := 100.0;
	y_min : LREAL := -100.0;
END_VAR

//-----------------------------------------------------------------------------------------

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
    Axis         := axis_x,
    Execute      := (state = 1) AND power_x.Status,
    Position     := target_x,
    Velocity     := vel_x,
    Acceleration := acc_x,
    Deceleration := dec_x,
    Jerk         := jrk_x);

move_y(
    Axis         := axis_y,
    Execute      := (state = 1) AND power_y.Status,
    Position     := target_y,
    Velocity     := vel_y,
    Acceleration := acc_y,
    Deceleration := dec_y,
    Jerk         := jrk_y);

CASE state OF
    0: // WAIT FOR TARGET
        IF execute THEN
            IF target_x <= x_max AND target_x >= x_min AND target_y <= y_max AND target_y >= y_min THEN

                dx   := ABS(target_x - axis_x.NcToPlc.ActPos);
                dy   := ABS(target_y - axis_y.NcToPlc.ActPos);
                dist := SQRT(dx*dx + dy*dy);

                IF dist < min_dist THEN
                    execute := FALSE;
                ELSE
                    kx := dx / dist;
                    ky := dy / dist;

                    vel_x := MAX(velocity     * kx, min_param);
                    vel_y := MAX(velocity     * ky, min_param);
                    acc_x := MAX(acceleration * kx, min_param);
                    acc_y := MAX(acceleration * ky, min_param);
                    dec_x := MAX(deceleration * kx, min_param);
                    dec_y := MAX(deceleration * ky, min_param);
                    jrk_x := MAX(jerk         * kx, min_param);
                    jrk_y := MAX(jerk         * ky, min_param);

                    state := 1;
                END_IF
            ELSE
                state := 3;
            END_IF
        END_IF

    1: // MOVE
        IF move_x.Done AND move_y.Done THEN
            state := 2;
        ELSIF move_x.Error OR move_y.Error OR move_x.CommandAborted OR move_y.CommandAborted THEN
            state := 3;
        END_IF

    2: // MOVEMENT DONE
        execute := FALSE;
        state   := 0;

    3: // ERROR
        execute := FALSE;
END_CASE