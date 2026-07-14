---
title: Cristian Clock Synchronization
author: Group 3
theme:
  name: dark
  override:
    default:
      title:
        font_size: 3
      colors:
        background: "09090F"
        foreground: "EBDBB2"
    code:
      theme_name: gruvbox-dark
      padding:
        horizontal: 2
        vertical: 1
      background: false
    palette:
      colors:
        black: "282828"
        red: "CC241D"
        green: "98971A"
        yellow: "D79921"
        blue: "458588"
        purple: "B16286"
        aqua: "689D6A"
        orange: "D65D0E"
        gray: "A89984"
        light_red: "FB4934"
        light_green: "B8BB26"
        light_yellow: "FABD2F"
        light_blue: "83A598"
        light_purple: "D3869B"
        light_aqua: "8EC07C"
        light_orange: "FE8019"

---
Cristian's Algorithm
---
# Cristian's Algorithm
```latex +render
\[ \mathbb{N}\]
```


<!-- end_slide -->

# Headers

Each header type can be styled differently.

## Subheaders

### And more

<!-- end_slide -->

Code highlighting
---

Highlight code in 50+ programming languages:

```rust
// Rust
fn greet() -> &'static str {
    "hi mom"
}
```

```python
# Python
def greet() -> str:
    return "hi mom"
```

<!-- pause -->

-------

Code snippets can have different styles including no background:

```cpp +no_background +line_numbers
// C++
string greet() {
    return "hi mom";
}
```

<!-- end_slide -->

Dynamic code highlighting
---

Dynamically highlight different subsets of lines:

```python {1-4|6-10|all} +line_numbers +exec
#!/usr/bin/env python3

from datetime import datetime
import socket
import threading

def return_time(client_sock, addr):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    client_sock.sendall(current_time.encode())

def main():
    server_addr = 42069
    server      = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', server_addr))
    server.listen(socket.SOMAXCONN)
    print(f"Listening on localhost:{server_addr}")
    while True:
        client_sock, addr = server.accept()
        print(f"\nConnection from {addr}")
        client_thread = threading.Thread(target=return_time, args=(client_sock, addr))
        client_thread.daemon = True
        client_thread.start()
main()
```

<!-- end_slide -->

Client Code
---

```python +exec
import socket
from datetime import datetime, timedelta

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 42069))
    now = datetime.now() 
    print(f"TO = {now.time()}")
    date_string = client.recv(1024).decode()
    parsed_time = datetime.strptime(date_string, "%H:%M:%S").time()
    print(f"T1 = {parsed_time}")
    dt_object = datetime.combine(now.date(), parsed_time)
    td = int((abs(dt_object - now)).total_seconds())
    print(f"T1 - T0 = {td}")
    rtt = td // 2
    print(f"RTT = {rtt}")
    synchronized_client_time = dt_object + timedelta(seconds=td)
    print(f"Synchronized time {synchronized_client_time.time()}")
main()
```

<!-- end_slide -->

Images
---

Images and animated gifs are supported in terminals such as:

* kitty
* iterm2
* wezterm
* ghostty
* foot
* Any sixel enabled terminal

<!-- column_layout: [1, 3, 1] -->

<!-- column: 1 -->


_Picture by Alexis Bailey / CC BY-NC 4.0_

<!-- end_slide -->

Column layouts
---

<!-- column_layout: [7, 3] -->

<!-- column: 0 -->

Use column layouts to structure your presentation:

* Define the number of columns.
* Adjust column widths as needed.
* Write content into every column.

```rust
fn potato() -> u32 {
    42
}
```

<!-- column: 1 -->


<!-- reset_layout -->

---

Layouts can be reset at any time.

```python
print("Hello world!")
```

<!-- end_slide -->

Text formatting
---

Text formatting works including:

* **Bold text**.
* _Italics_.
* **_Bold and italic_**.
* ~Strikethrough~.
* `Inline code`.
* Links [](https://example.com/)
* <span style="color: red">Colored</span> text.
* <span style="color: blue; background-color: black">Background color</span> can be changed too.

<!-- end_slide -->

More markdown
---

Other markdown elements supported are:

# Block quotes

> Lorem ipsum dolor sit amet. Eos laudantium animi ut ipsam beataeet
> et exercitationem deleniti et quia maiores a cumque enim et
> aspernatur nesciunt sed adipisci quis.

# Alerts

> [!caution]
> Github style alerts

# Tables

| Name   | Taste  |
| ------ | ------ |
| Potato | Great  |
| Carrot | Yuck   |

<!-- end_slide -->

<!-- jump_to_middle -->

The end
---
