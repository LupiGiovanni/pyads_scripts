PROGRAM MAIN
VAR
    axis : AXIS_REF;
    power : MC_Power;
    move : MC_MoveRelative;

    distance : LREAL := 0;
    velocity : LREAL := 1.0;

    execute : BOOL := FALSE;
    state : INT := 0;
END_VAR

//-------------------------------------------------------

axis.ReadStatus();

power(
    Axis            := axis,
    Enable          := TRUE,
    Enable_Positive := TRUE,
    Enable_Negative := TRUE,
    Override        := 100);

move(
    Axis := axis,
    Execute := (state=1) AND power.Status,
    Distance := distance,
    Velocity := velocity);

CASE state OF
    0: // wait for command
        IF execute THEN
            state := 1;
        END_IF

    1: // move
        IF move.Done THEN
            state := 2;
        ELSIF move.Error OR move.CommandAborted THEN
            state := 3;
        END_IF

    2: // movement done
        execute := FALSE;
        state := 0;

    3: // error
        execute := FALSE;
END_CASE