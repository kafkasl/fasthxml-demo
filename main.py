from fasthtml.common import *
from fasthtml.components import Doc, Screen, View, Text, Text_Field, Behavior, Styles, Switch
db = database('data/utodos.db')
class Todo: id:int; title:str; done:bool; details:str; priority:int
todos = db.create(Todo, transform=True)

# The style can't be auto-created by default due to the non-default id, have a look
def Style(id, **kwargs): return FT('style', (), {'id': id, **kwargs})

app,rt = fast_app()

def render_to_response(component):
    """Render component to Hyperview XML response"""
    content = to_xml(component)
    response = Response(content)
    response.headers['Content-Type'] = 'application/vnd.hyperview+xml'
    return response

def Header(*c, **kwargs): return FT('header', c, kwargs)

def Layout(header_content=None, main_content=None):
    """Base layout for all Hyperview screens"""
    return Doc(
        Screen(
            Styles(
                Style(id="body", flex="1", backgroundColor="#f9fafb"),
                Style(id="header", backgroundColor="#3b82f6", padding="16", paddingTop="48"),
                Style(id="header-title", fontSize="24", fontWeight="bold", color="#ffffff"),
                Style(id="main", flex="1", padding="16"),
                Style(id="button", backgroundColor="#3b82f6", color="#ffffff", 
                      paddingHorizontal="20", paddingVertical="10", 
                      borderRadius="6", fontWeight="600", textAlign="center",
                      alignSelf="flex-start"),
                Style(id="todo-item", flexDirection="row", justifyContent="space-between", 
                      alignItems="center", paddingVertical="8"),
                Style(id="todo-text", flex="1"),
                Style(id="todo-actions", flexDirection="row", gap="8"),
                Style(id="edit-button", backgroundColor="#10b981", color="#ffffff", 
                      paddingHorizontal="12", paddingVertical="6", 
                      borderRadius="4", fontSize="14"),
                Style(id="delete-button", backgroundColor="#ef4444", color="#ffffff", 
                      paddingHorizontal="12", paddingVertical="6", 
                      borderRadius="4", fontSize="14"),
                Style(id="text-field", borderWidth="1", borderColor="#d1d5db", 
                      borderRadius="4", padding="8", backgroundColor="#ffffff",
                      fontSize="16"),
                Style(id="form-row", flexDirection="row", alignItems="center", 
                      justifyContent="space-between", marginBottom="12"),
                Style(id="label", fontSize="16", color="#374151")
            ),
            Body(
                Header(
                    header_content or Text("Contact.app", style="header-title"),
                    style="header"
                ),
                View(main_content, style="main"),
                style="body", safe_area="true"
            )
        ),
        xmlns="https://hyperview.org/hyperview"
    )



def TodoEditItem(todo):
    """Render todo item in edit mode"""
    return Form(
        View(
            Text_Field(name="title", value=todo.title, style="text-field"),
            View(
                Text("Done", style="label"),
                Switch(name="done", value="on", selected="true" if todo.done else "false"),
                style="form-row"
            ),
            View(
                Text(
                    Behavior(trigger="press", verb="post", href=f"/todo/{todo.id}/edit", action="replace", target=f"todo-{todo.id}"),
                    "Save",
                    style="edit-button"
                ),
                Text(
                    Behavior(trigger="press", verb="get", href=f"/todo/{todo.id}", action="replace", target=f"todo-{todo.id}"),
                    "Cancel",
                    style="delete-button"
                ),
                style="todo-actions"
            ),
            style="todo-item"
        ),
        id=f"todo-{todo.id}",
        xmlns="https://hyperview.org/hyperview"
    )


def clr_details(): return ""

@rt
def update(todo: Todo): return todos.update(todo), clr_details()

@rt
def edit(id:int):
    res = Form(hx_post=update, target_id=f'todo-{id}', id="edit")(
        Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), CheckboxX(id="done", label='Done'),
        Textarea(id="details", name="details", rows=10))
    return fill_form(res, todos[id])

@rt
def rm(id:int):
    todos.delete(id)
    return clr_details()

@rt
def show(id:int):
    todo = todos[id]
    btn = Button('delete', hx_post=rm.to(id=todo.id),
                 hx_target=f'#todo-{todo.id}', hx_swap="outerHTML")
    return Div(H2(todo.title), Div(todo.details, cls="marked"), btn)

@patch
def __ft__(self:Todo):
    """Render Todo as Hyperview XML"""
    return View(
        Text(f"{'✅ ' if self.done else ''}{self.title}", style="todo-text"),
        View(
            Text(
                Behavior(trigger="press", verb="get", href=f"/todo/{self.id}/edit", 
                        action="replace", target=f"todo-{self.id}"),
                "Edit",
                style="edit-button"
            ),
            Text(
                Behavior(trigger="press", verb="post", href=f"/delete/{self.id}", 
                        action="replace", target=f"todo-{self.id}"),
                "Delete",
                style="delete-button"
            ),
            style="todo-actions"
        ),
        id=f"todo-{self.id}",
        style="todo-item",
        xmlns="https://hyperview.org/hyperview"
    )

@rt("/create")
def create(title: str):
    if not title:
        return render_to_response(View(xmlns="https://hyperview.org/hyperview"))  # Empty view
    todo = todos.insert(Todo(title=title, done=False, priority=len(todos())))
    return render_to_response(todo)  # Uses Todo.__ft__


@rt("/todo/{id:int}")
def show_todo(id: int):
    """Show todo in view mode"""
    todo = todos[id]
    return render_to_response(todo)  # Uses Todo.__ft__

@rt("/todo/{id:int}/edit", methods=['GET'])
def edit_todo_get(id: int):
    """Show todo in edit mode"""
    todo = todos[id]
    return render_to_response(TodoEditItem(todo))

@rt("/todo/{id:int}/edit", methods=['POST'])
def edit_todo_post(id: int, title: str, done: str = "false"):
    """Save todo edits"""
    print(f"Received: title='{title}', done='{done}'")
    todo = todos[id]
    todo.title = title
    todo.done = 1 if done == "on" else 0  # Switch sends "on" when checked
    todos.update(todo)
    print(f"Updated todo: {todo}")
    # Return the todo in view mode after saving
    return render_to_response(todo)  # Uses Todo.__ft__

@rt("/delete/{id:int}")
def delete_todo(id: int):
    todos.delete(id)
    # Return empty response - the client will remove the element
    return render_to_response(View(xmlns="https://hyperview.org/hyperview"))

@rt("/hyperview")
def index():
    todo_items = todos(order_by='priority')
    
    main_content = View(
        Form(
            Text_Field(name="title", placeholder="New Todo", style="text-field"),
            Text(
                Behavior(trigger="press", verb="post", href="/create", 
                        action="append", target="todo-list"),
                "Add Todo",
                style="button"
            )
        ),
        View(*todo_items, id="todo-list")
    )
    
    return render_to_response(
        Layout(
            header_content=Text("Todo list", style="header-title"),
            main_content=main_content
        )
    )

serve()
