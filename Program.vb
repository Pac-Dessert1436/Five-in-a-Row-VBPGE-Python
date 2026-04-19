Option Strict On
Option Infer On
Imports VbPixelGameEngine

Public NotInheritable Class Program
    Inherits PixelGameEngine

    Friend Enum Piece As Byte : Empty = 0 : Black = 1 : White = 2 : End Enum

    ' This game is played on a 15x15 game board; ensure five pieces in a row to win.
    Private Const GRID_SIZE As Integer = 15, WIN_COUNT As Integer = 5

    Private ReadOnly board(GRID_SIZE - 1, GRID_SIZE - 1) As Piece

    Private currPlayer As Piece, gameOver As Boolean, winner As Piece
    Private boardStartX As Integer, boardStartY As Integer, cellSize As Integer
    Private blackHasViolation As Boolean

    Private hoverPos As Vi2d, isWithinBoard As Boolean

    Public Sub New()
        AppName = "VBPGE Five-in-a-Row"
    End Sub

    Protected Overrides Function OnUserCreate() As Boolean
        ' Clear board and reset game state.
        Array.Clear(board, 0, board.Length)
        currPlayer = Piece.Black
        gameOver = False
        winner = Piece.Empty

        ' Calculate centered board position.
        cellSize = Math.Min(ScreenWidth, ScreenHeight) \ (GRID_SIZE + 2)
        boardStartX = (ScreenWidth - GRID_SIZE * cellSize) \ 2
        boardStartY = (ScreenHeight - GRID_SIZE * cellSize) \ 2
        Return True
    End Function

    Protected Overrides Function OnUserUpdate(elapsedTime As Single) As Boolean
        Clear(Presets.DarkGreen)

        If GetKey(Key.R).Pressed Then Call OnUserCreate()
        DrawBoard()
        DrawString(80, 575, "Ensure 5 pieces in a row to win the game.", Presets.White, 2)
        If Not gameOver Then
            DrawString(360, 10, "Left-click to place pieces.", Presets.White, 2)
            HandlePlayerTurn()
        Else
            Dim resultMessage = If(winner = Piece.Black, "BLACK WINS!", "WHITE WINS!")
            DrawString(11, 11, resultMessage, Presets.Gray, 4)
            DrawString(10, 10, resultMessage, Presets.Snow, 4)
            DrawString(11, 61, "Press ""R"" to restart", Presets.Gray, 2)
            DrawString(10, 60, "Press ""R"" to restart", Presets.Snow, 2)
        End If

        Dim hoverX = (GetMouseX - boardStartX) \ cellSize
        Dim hoverY = (GetMouseY - boardStartY) \ cellSize

        isWithinBoard = hoverX >= 0 AndAlso hoverX < GRID_SIZE AndAlso
            hoverY >= 0 AndAlso hoverY < GRID_SIZE
        hoverPos = If(isWithinBoard, New Vi2d(hoverX, hoverY), New Vi2d(-1, -1))

        Return Not GetKey(Key.ESCAPE).Pressed
    End Function

    Private Sub DrawBoard()
        Dim markers As New List(Of Vi2d) From {New Vi2d(3, 3), New Vi2d(3, 11), New Vi2d(7, 7),
            New Vi2d(11, 3), New Vi2d(11, 11)}

        ' Draw grid lines and markers.
        For i As Integer = 0 To GRID_SIZE - 1
            Dim x = boardStartX + i * cellSize + cellSize \ 2
            Dim y = boardStartY + i * cellSize + cellSize \ 2

            ' Draw horizontal grid lines.
            Dim x1 = boardStartX + cellSize \ 2
            Dim x2 = boardStartX + GRID_SIZE * cellSize - cellSize \ 2
            DrawLine(x1, y, x2, y, Presets.Gray)

            ' Draw vertical grid lines.
            Dim y1 = boardStartY + cellSize \ 2
            Dim y2 = boardStartY + GRID_SIZE * cellSize - cellSize \ 2
            DrawLine(x, y1, x, y2, Presets.Gray)
        Next i
        For Each p As Vi2d In markers
            Dim x = boardStartX + p.x * cellSize + cellSize \ 2
            Dim y = boardStartY + p.y * cellSize + cellSize \ 2
            FillCircle(x, y, 4, Presets.Gray)
        Next p

        ' Draw black and white pieces.
        For x As Integer = 0 To GRID_SIZE - 1
            For y As Integer = 0 To GRID_SIZE - 1
                Dim pieceX = boardStartX + x * cellSize + cellSize \ 2
                Dim pieceY = boardStartY + y * cellSize + cellSize \ 2

                Select Case board(x, y)
                    Case Piece.Black
                        FillCircle(pieceX, pieceY, cellSize \ 2 - 2, Presets.Black)
                    Case Piece.White
                        FillCircle(pieceX, pieceY, cellSize \ 2 - 2, Presets.White)
                End Select
            Next y
        Next x

        If Not isWithinBoard Then Exit Sub
        If board(hoverPos.x, hoverPos.y) = Piece.Empty AndAlso Not gameOver Then
            Dim x = boardStartX + hoverPos.x * cellSize + cellSize \ 2
            Dim y = boardStartY + hoverPos.y * cellSize + cellSize \ 2
            DrawCircle(x, y, cellSize \ 4, Presets.Yellow)
        End If
    End Sub

    Private Sub HandlePlayerTurn()
        ' Display current player.
        Dim message = If(currPlayer = Piece.Black, "< BLACK'S TURN >", "< WHITE'S TURN >")
        DrawString(10, 10, message, Presets.Yellow, 2)

        ' Display violation message if black has a violation
        If blackHasViolation Then
            DrawString(10, 40, "BLACK VIOLATION! WHITE'S TURN", Presets.Red, 2)
        End If

        ' Handle mouse click.
        If GetMouse(0).Released Then
            ' Get the mouse position and then convert to grid coordinates.
            Dim gridX = (GetMouseX - boardStartX) \ cellSize
            Dim gridY = (GetMouseY - boardStartY) \ cellSize

            ' Validate moves, place piece, and check win condition.
            If gridX >= 0 AndAlso gridX < GRID_SIZE AndAlso gridY >= 0 AndAlso
                gridY < GRID_SIZE AndAlso board(gridX, gridY) = 0 Then

                ' Check professional rules for black pieces
                If currPlayer = Piece.Black Then
                    ' Temporarily place the piece to check for violations
                    board(gridX, gridY) = currPlayer
                    Dim hasViolation = CheckBlackViolations(gridX, gridY)
                    board(gridX, gridY) = Piece.Empty

                    If hasViolation Then
                        blackHasViolation = True
                        ' Skip black's turn due to violation
                        currPlayer = Piece.White
                        Exit Sub
                    End If
                End If

                board(gridX, gridY) = currPlayer
                If CheckWin(gridX, gridY) Then
                    gameOver = True
                    winner = currPlayer
                End If

                ' Switch player and reset violation state in time.
                If currPlayer = Piece.Black Then
                    currPlayer = Piece.White
                Else
                    blackHasViolation = False
                    currPlayer = Piece.Black
                End If
            End If
        End If
    End Sub

    Private Function CheckBlackViolations(x As Integer, y As Integer) As Boolean
        Return CheckOverline(x, y) OrElse CheckDoubleThree(x, y) OrElse CheckDoubleFour(x, y)
    End Function

    Private Function CheckOverline(x As Integer, y As Integer) As Boolean
        Dim dirs = {New Vi2d(1, 0), New Vi2d(0, 1), New Vi2d(1, 1), New Vi2d(1, -1)}
        Dim player As Piece = board(x, y)

        For Each d As Vi2d In dirs
            Dim count As Integer = 1 ' Current piece

            ' Check positive direction
            For i As Integer = 1 To 5 ' Check up to 5 pieces beyond win condition
                Dim nx As Integer = x + d.x * i, ny As Integer = y + d.y * i
                If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE OrElse
                    board(nx, ny) <> player Then Exit For
                count += 1
            Next i

            ' Check negative direction
            For i As Integer = 1 To 5 ' Check up to 5 pieces beyond win condition
                Dim nx As Integer = x - d.x * i, ny As Integer = y - d.y * i
                If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE OrElse
                    board(nx, ny) <> player Then Exit For
                count += 1
            Next i

            If count > 5 Then Return True
        Next d

        Return False
    End Function

    Private Function CheckDoubleThree(x As Integer, y As Integer) As Boolean
        Dim dirs = {New Vi2d(1, 0), New Vi2d(0, 1), New Vi2d(1, 1), New Vi2d(1, -1)}
        Dim player As Piece = board(x, y)
        Dim threeCount As Integer = 0

        For Each d As Vi2d In dirs
            ' Check for open three in this direction
            If IsOpenThree(x, y, d, player) Then
                threeCount += 1
                If threeCount >= 2 Then Return True
            End If
        Next d

        Return False
    End Function

    Private Function CheckDoubleFour(x As Integer, y As Integer) As Boolean
        Dim dirs = {New Vi2d(1, 0), New Vi2d(0, 1), New Vi2d(1, 1), New Vi2d(1, -1)}
        Dim player As Piece = board(x, y)
        Dim fourCount As Integer = 0

        For Each d As Vi2d In dirs
            ' Check for open four in this direction
            If IsOpenFour(x, y, d, player) Then
                fourCount += 1
                If fourCount >= 2 Then Return True
            End If
        Next d

        Return False
    End Function

    Private Function IsOpenThree(x As Integer, y As Integer, dir As Vi2d, player As Piece) As Boolean
        ' Check if the current position forms an open three in the given direction
        Dim count As Integer = 1
        Dim openEnds As Integer = 0

        ' Check positive direction
        For i As Integer = 1 To 3
            Dim nx As Integer = x + dir.x * i, ny As Integer = y + dir.y * i
            If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE Then
                Exit For
            End If
            If board(nx, ny) = player Then
                count += 1
            ElseIf board(nx, ny) = Piece.Empty Then
                openEnds += 1
                Exit For
            Else
                Exit For
            End If
        Next i

        ' Check negative direction
        For i As Integer = 1 To 3
            Dim nx As Integer = x - dir.x * i, ny As Integer = y - dir.y * i
            If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE Then
                Exit For
            End If
            If board(nx, ny) = player Then
                count += 1
            ElseIf board(nx, ny) = Piece.Empty Then
                openEnds += 1
                Exit For
            Else
                Exit For
            End If
        Next i

        ' Open three has exactly 3 pieces and 2 open ends
        Return count = 3 AndAlso openEnds = 2
    End Function

    Private Function IsOpenFour(x As Integer, y As Integer, dir As Vi2d, player As Piece) As Boolean
        ' Check if the current position forms an open four in the given direction
        Dim count As Integer = 1
        Dim openEnds As Integer = 0

        ' Check positive direction
        For i As Integer = 1 To 4
            Dim nx As Integer = x + dir.x * i, ny As Integer = y + dir.y * i
            If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE Then
                Exit For
            End If
            If board(nx, ny) = player Then
                count += 1
            ElseIf board(nx, ny) = Piece.Empty Then
                openEnds += 1
                Exit For
            Else
                Exit For
            End If
        Next i

        ' Check negative direction
        For i As Integer = 1 To 4
            Dim nx As Integer = x - dir.x * i, ny As Integer = y - dir.y * i
            If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE Then
                Exit For
            End If
            If board(nx, ny) = player Then
                count += 1
            ElseIf board(nx, ny) = Piece.Empty Then
                openEnds += 1
                Exit For
            Else
                Exit For
            End If
        Next i

        ' Open four has exactly 4 pieces and 2 open ends
        Return count = 4 AndAlso openEnds = 2
    End Function

    Private Function CheckWin(x As Integer, y As Integer) As Boolean
        ' Directions: Horizontal, Vertical, Diagonal \, Diagonal /
        Dim dirs = {New Vi2d(1, 0), New Vi2d(0, 1), New Vi2d(1, 1), New Vi2d(1, -1)}
        Dim player As Piece = board(x, y)

        For Each d As Vi2d In dirs
            Dim count As Integer = 1 ' Current piece.

            ' Check positive direction.
            For i As Integer = 1 To WIN_COUNT - 1
                Dim nx As Integer = x + d.x * i, ny As Integer = y + d.y * i
                If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE OrElse
                    board(nx, ny) <> player Then Exit For
                count += 1
            Next i

            ' Check negative direction.
            For i As Integer = 1 To WIN_COUNT - 1
                Dim nx As Integer = x - d.x * i, ny As Integer = y - d.y * i
                If nx < 0 OrElse nx >= GRID_SIZE OrElse ny < 0 OrElse ny >= GRID_SIZE OrElse
                    board(nx, ny) <> player Then Exit For
                count += 1
            Next i

            If count >= WIN_COUNT Then Return True
        Next d

        Return False
    End Function

    Friend Shared Sub Main()
        With New Program
            If .Construct(screenW:=800, screenH:=600, fullScreen:=True) Then .Start()
        End With
    End Sub
End Class