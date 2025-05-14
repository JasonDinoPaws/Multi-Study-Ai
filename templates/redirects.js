const istemp = window.location.href.search("templates") != -1

function redirect(name)
{
    console.log(name)
    if (!istemp && name == "index")
    {
        name = ""
    }
    window.location.href =  (istemp? name+".html": name);
}