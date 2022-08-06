import {Link, Outlet, useLocation} from "react-router-dom";

function HeaderLink({to, children}) {
    const {pathname} = useLocation();
    const linkClassName = pathname === to ? 'text-lime-600' : '';

    return <div className="inline-flex px-3 py-2">
        <Link to={to} className={linkClassName}>{children}</Link>
    </div>
}

export default function JudgeLayout() {
    return <div className={'max-w-7xl mx-auto'}>
        <div className="flex justify-between px-3 py-4">
            <div className="px-3">
                <Link to="/">
                    <div className="h-10 w-20 bg-lime-600 text-white text-xl font-bold rounded flex justify-center items-center">NFO</div>
                </Link>
            </div>
            <div className="">
                <HeaderLink to={'/login'}>Logout</HeaderLink>
            </div>
        </div>

        <Outlet/>
    </div>
}