import lily

t_array = lily.note.NoteArray(initial_clef="treble", transposition="f c'")
t_array.create_note(8, 10, "^>")
t_array.create_note(1, 4, "", "", True)
t_array.create_note(0, 14)

test_note = lily.note.Note(8, 4)
test_note.add_articulation(4)
t_array.add_note(test_note)
t_array.create_note(18, 0, dynamic='f')
t_array.create_note(9, 0)
t_array.create_spanner(spanner_type='dim', apply_type='start')
t_array.create_note([9, 10, 11], 0)
t_array.create_spanner(spanner_type='slur', apply_type='start')
t_array.create_note(2, 0)
t_array.create_clef('bass')
t_array.create_note(-5, 7)
t_array.create_spanner(spanner_type='dim', apply_type='stop')
t_array.create_note([3, 7], 10)
t_array.create_spanner(spanner_type='slur', apply_type='stop')
t_score1 = lily.score.Score(t_array)

t_file = lily.lilypond_file.LilypondFile()
t_file.add_score(t_score1)

t_file.save_and_render("DidItWork", view_image=True, autocrop=True)

print("Done")
