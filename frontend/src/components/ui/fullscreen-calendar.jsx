import React, { useState, useMemo } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "./button"
import { cn } from "@/lib/utils"

const MONTHS = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

const DAYS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]

function classNames(...classes) {
  return classes.filter(Boolean).join(" ")
}

export function FullscreenCalendar({ data = [] }) {
  const today = new Date()
  const [currentDate, setCurrentDate] = useState(today)

  const currentMonth = currentDate.getMonth()
  const currentYear = currentDate.getFullYear()

  const firstDayOfMonth = new Date(currentYear, currentMonth, 1)
  const lastDayOfMonth = new Date(currentYear, currentMonth + 1, 0)
  const daysInMonth = lastDayOfMonth.getDate()
  const startingDayOfWeek = firstDayOfMonth.getDay()

  const previousMonth = () => {
    setCurrentDate(new Date(currentYear, currentMonth - 1, 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentYear, currentMonth + 1, 1))
  }

  const goToToday = () => {
    setCurrentDate(today)
  }

  const calendarDays = useMemo(() => {
    const days = []
    
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push({ day: null, events: [] })
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentYear, currentMonth, day)
      const dayData = data.find((d) => {
        const dataDate = new Date(d.day)
        return (
          dataDate.getDate() === day &&
          dataDate.getMonth() === currentMonth &&
          dataDate.getFullYear() === currentYear
        )
      })

      days.push({
        day,
        date,
        events: dayData ? dayData.events : [],
        isToday:
          day === today.getDate() &&
          currentMonth === today.getMonth() &&
          currentYear === today.getFullYear(),
      })
    }

    return days
  }, [currentMonth, currentYear, data, daysInMonth, startingDayOfWeek, today])

  return (
    <div className="flex h-full flex-col">
      <header className="flex items-center justify-between border-b border-gray-200 px-6 py-4 lg:flex-none">
        <div className="flex items-center gap-4">
          <div className="relative flex items-center rounded-full bg-gray-900 px-3 py-1.5 text-xs font-medium text-white">
            {today.getDate()} {MONTHS[today.getMonth()].slice(0, 3)}
          </div>
          <h1 className="text-base font-semibold text-gray-900">
            <time dateTime={currentDate.toISOString()}>
              {MONTHS[currentMonth]} {currentYear}
            </time>
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={goToToday}
            className="text-sm"
          >
            Hoy
          </Button>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={previousMonth}
              className="h-8 w-8"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={nextMonth}
              className="h-8 w-8"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex flex-auto flex-col overflow-auto bg-white">
        <div className="sticky top-0 z-10 grid grid-cols-7 gap-px border-b border-gray-300 bg-gray-200 text-center text-xs font-semibold text-gray-700">
          {DAYS.map((day) => (
            <div key={day} className="bg-white py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="flex flex-auto">
          <div className="grid w-full grid-cols-7 grid-rows-6 gap-px bg-gray-200">
            {calendarDays.map((day, dayIdx) => (
              <div
                key={dayIdx}
                className={classNames(
                  day.day && "bg-white",
                  !day.day && "bg-gray-50",
                  "relative px-3 py-2"
                )}
              >
                <time
                  dateTime={day.date ? day.date.toISOString() : undefined}
                  className={classNames(
                    day.isToday && "flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 font-semibold text-white",
                    "ml-auto text-xs"
                  )}
                >
                  {day.day}
                </time>
                
                {day.events && day.events.length > 0 && (
                  <ol className="mt-2 space-y-1">
                    {day.events.slice(0, 2).map((event) => (
                      <li key={event.id}>
                        <a
                          href="#"
                          className="group flex rounded-md p-2 transition-colors hover:bg-gray-100"
                          onClick={(e) => e.preventDefault()}
                        >
                          <div className="flex-auto truncate text-xs">
                            <p className="font-medium text-gray-900">{event.name}</p>
                            <time
                              dateTime={event.datetime}
                              className="text-gray-500"
                            >
                              {event.time}
                            </time>
                          </div>
                        </a>
                      </li>
                    ))}
                    {day.events.length > 2 && (
                      <li className="text-xs text-gray-500">
                        + {day.events.length - 2} más
                      </li>
                    )}
                  </ol>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
