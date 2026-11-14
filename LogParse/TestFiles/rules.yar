rule ExampleRule {
    strings:
        $magic_string = "ExampleString"
    condition:
        $magic_string
}
rule AnotherRule {
    strings:
        $another_string = "AnotherString"
    condition:
        $another_string
}
