Gremlin.defineStep('argumentToAtomName', [Vertex,Pipe], {
	_()
	.children().loop(1){!(it.object.type in ['Identifier', 'MemberAccess', 'PtrMemberAccess'])}
});

Gremlin.defineStep('callToLVal', [Vertex,Pipe], {
	_()
	.parents().loop(1){true}{it.object.type == 'AssignmentExpr'}
	.lval()
});

Gremlin.defineStep('symbolToUsingConditions', [Vertex, Pipe], {
	_() // Symbol node
	.in('USE', 'DEF')
	.ifThenElse{it.type == 'Condition'}
		{it}
		{it.parents().loop(1){true}{it.object.type == 'Condition'}}
});

Gremlin.defineStep('taintUpwards', [Vertex, Pipe], {
	_() // Symbol node
	.copySplit(
		_(),
		_().in('DEF')
		.filter{it.isCFGNode == 'True'}
		.out('USE')
		.simplePath()
		.loop(4){it.loops < 5}{true}
	).fairMerge()
	.dedup()
});

Gremlin.defineStep('taintDownwards', [Vertex, Pipe], {
	_() // Symbol node
	.copySplit(
		_(),
		_().in('USE')
		.filter{it.isCFGNode == 'True'}
		.out('DEF')
		.simplePath()
		.loop(4){it.loops < 5}{true}
	).fairMerge()
	.dedup()
});

Gremlin.defineStep('forwardSlice', [Vertex, Pipe], { symbols,
                     ORDER = 5, edgeTypes = ['REACHES', 'CONTROLS'] ->
        _()
        .copySplit(
                _(),
                _().sideEffect{first = true;}.as('x')
                .transform{
                          it.outE(*edgeTypes)
                          .filter{it.label == 'CONTROLS' || !first || it.var in symbols}
                          .inV().gather{it}.scatter()
                          .sideEffect{first = false}
                }.scatter()
                .loop('x'){it.loops <= ORDER}{true}
        ).fairMerge()
        .dedup()
});


Gremlin.defineStep('backwardSlice', [Vertex, Pipe], { symbols,
                     ORDER = 5, edgeTypes = ['REACHES', 'CONTROLS'] ->
        _()
        .copySplit(
                _(),
                _()
                .sideEffect{first = true;}.as('x')
                .transform{
                        it.inE(*edgeTypes)
                        .filter{it.label == 'CONTROLS' || !first || it.var in symbols}
                        .outV().gather{it}.scatter()
                        .sideEffect{first = false}
                }.scatter()
                .loop('x'){it.loops <= ORDER}{true}
        ).fairMerge()
        .dedup()
});


Gremlin.defineStep('statementToSinks', [Vertex, Pipe], { symbol ->
	_()
	.sideEffect{first = true}
	.outE('REACHES')
	.filter{it.var == symbol || !first}
	.sideEffect{v = it.var}
	.sideEffect{first = false}
	.inV()
	.loop(5){it.loops < 5}{true}
	.dedup()
	.astNodes()
	.filter{it.type in ['CallExpression']}
	.ifThenElse{it.type == 'CallExpression'}
		{
		it.sideEffect{call = it}
		.callToArguments()
		.sideEffect{argNum = it.childNum}
		.uses()
		.filter{it.code == v}
		.transform{call}
		.callToCallee()
		.transform{it.code + ":" + argNum}
		}
		{it.type}
	.dedup()
});
