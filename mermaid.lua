-- Quarto renders only `{mermaid}` cells, and GitHub only `mermaid` fences.
function CodeBlock(block)
  if not block.classes:includes("mermaid") then
    return
  end
  local dir = os.getenv("QUARTO_SHARE_PATH") .. "/formats/html/mermaid/"
  quarto.doc.add_html_dependency({
    name = "quarto-diagram",
    scripts = {
      dir .. "mermaid.min.js",
      { path = dir .. "mermaid-init.js", afterBody = true },
    },
  })
  block.classes:insert("mermaid-js")
  -- mermaid-init.js moves the diagram to the end of the parent element.
  return pandoc.Div(block)
end
