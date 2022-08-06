import {useEffect, useState} from 'react';

export default function JudgeWordNet() {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [item, setItem] = useState({});
    const [items, setItems] = useState([
        {
            id: 1,
            word: 'gula',
            hypernyms: [{word: 'carbohydrate', definition: 'xxx'}, {
                word: 'sweetener',
                definition: 'additive to alter taste of food or drink'
            }]
        },
        {id: 2, word: 'garam', hypernyms: [{word: 'crystal', definition: 'xxx'}]},
        {id: 3, word: 'lada', hypernyms: [{word: 'spice', definition: 'xxx'}]},
    ]);

    useEffect(() => {
        setItem(items[currentIndex]);
    }, [currentIndex]);

    return <div className="mx-6 p-6 bg-lime-100 rounded">
        <div className="mb-4">
            <div className="rounded h-2 bg-white mb-1">
                <div className="h-2 rounded bg-lime-500"
                     style={{width: `${100 * (currentIndex + 1) / items.length}%`}}/>
            </div>
            <div className="text-sm text-lime-900 text-center">{currentIndex + 1} of {items.length}</div>
        </div>

        <h1 className="text-center text-xl font-bold mb-3 uppercase">{item.word}</h1>

        <div className="mb-3">Please select or suggest a correct hypernym:</div>

        {item.hypernyms?.map(nym => {
            return <div className="bg-lime-500 rounded text-white p-3 mb-3 cursor-pointer hover:opacity-75">
                <strong>{nym.word}</strong>,
                <span className="italic">definition: {nym.definition}</span>
            </div>
        })}

        <div className="mt-5">Suggest a hypernym:</div>
        <input type="text" className="w-full rounded px-3 my-2 py-1" name=""></input>

        <div className="mt-3">
            <button onClick={() => setCurrentIndex(n => n === 0 ? 0 : n - 1)}
                    disabled={currentIndex === 0}
                    className="btn rounded text-white bg-lime-500 mr-1 disabled:opacity-50">Prev
            </button>
            <button onClick={() => setCurrentIndex(n => n < items.length - 1 ? n + 1 : n)}
                    disabled={currentIndex === items.length - 1}
                    className="btn rounded text-white bg-lime-500 mr-1 disabled:opacity-50">Next
            </button>
        </div>

    </div>
}