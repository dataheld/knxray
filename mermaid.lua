-- Quarto renders only `{mermaid}` cells, and GitHub only `mermaid` fences.
function CodeBlock(block)
  if not block.classes:includes("mermaid") then
    return
  end
  local function path(file)
    return pandoc.path.join({
      os.getenv("QUARTO_SHARE_PATH"),
      "formats/html/mermaid",
      file,
    })
  end
  quarto.doc.add_html_dependency({
    name = "quarto-diagram",
    scripts = {
      path("mermaid.min.js"),
      { path = path("mermaid-init.js"), afterBody = true },
    },
  })
  block.classes:insert("mermaid-js")
  -- mermaid-init.js moves the diagram to the end of the parent element.
  return pandoc.Div(block)
end
